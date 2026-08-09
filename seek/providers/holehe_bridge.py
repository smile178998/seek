"""把 Holehe 的一百多个检测模块桥接成 seek 的 Provider。

Holehe 每个模块都是形如 `async def site(email, client, out)` 的协程，内部只用 httpx，
因此可以直接用 asyncio 调度，无需 Holehe 自带的 trio。这样就能复用 Holehe 持续维护的
站点端点，而不必自己手写、手动维护上百条规则。
"""

from __future__ import annotations

import asyncio
import logging
from typing import Any, Callable, Iterator

import httpx

from ..models import ProviderInfo, Result, Status
from .base import CheckContext, Provider, Timer

log = logging.getLogger(__name__)

# 明确属于「连不上」的 httpx 异常
_NETWORK_ERRORS = (
    httpx.ConnectError,
    httpx.ConnectTimeout,
    httpx.ReadTimeout,
    httpx.WriteTimeout,
    httpx.PoolTimeout,
    httpx.ProxyError,
    httpx.ReadError,
    httpx.RemoteProtocolError,
)


class _RecordingClient:
    """包一层记录每次请求的结果，用来还原 Holehe 内部吞掉的真实失败原因。

    Holehe 模块内部对所有异常统一标记为 rateLimit=True，导致「网络不通 / 被 403
    拦截 / 接口改版」全都显示成「被限流」。这里按顺序记录每个请求的状态码或异常，
    事后据此把兜底结果重新归类。其余属性（headers、cookies 等）透传给真实 client。
    """

    def __init__(self, client: httpx.AsyncClient) -> None:
        self._client = client
        self.events: list[tuple[str, Any]] = []

    def __getattr__(self, name: str) -> Any:
        # 只有真实 client 上存在的属性会走到这里（events/_client 已在实例字典中）
        return getattr(self._client, name)

    async def _do(self, method: str, *args: Any, **kwargs: Any) -> httpx.Response:
        try:
            resp = await getattr(self._client, method)(*args, **kwargs)
        except Exception as exc:  # 记录后原样抛出，交给 Holehe 自己的 except
            self.events.append(("error", exc))
            raise
        self.events.append(("status", resp.status_code))
        return resp

    async def get(self, *a: Any, **k: Any) -> httpx.Response:
        return await self._do("get", *a, **k)

    async def post(self, *a: Any, **k: Any) -> httpx.Response:
        return await self._do("post", *a, **k)

    async def put(self, *a: Any, **k: Any) -> httpx.Response:
        return await self._do("put", *a, **k)

    async def patch(self, *a: Any, **k: Any) -> httpx.Response:
        return await self._do("patch", *a, **k)

    async def delete(self, *a: Any, **k: Any) -> httpx.Response:
        return await self._do("delete", *a, **k)

    async def head(self, *a: Any, **k: Any) -> httpx.Response:
        return await self._do("head", *a, **k)

    async def options(self, *a: Any, **k: Any) -> httpx.Response:
        return await self._do("options", *a, **k)

    async def request(self, *a: Any, **k: Any) -> httpx.Response:
        return await self._do("request", *a, **k)


def _classify_failure(events: list[tuple[str, Any]]) -> tuple[Status, str]:
    """根据记录到的请求事件，把 Holehe 的兜底结果归类到真实原因。"""
    if not events:
        return Status.UNKNOWN, "模块未发出任何请求"

    kind, payload = events[-1]
    if kind == "error":
        if isinstance(payload, _NETWORK_ERRORS):
            return Status.ERROR, "网络无法连通（境外站点通常需配置 SEEK_PROXY 代理）"
        return Status.ERROR, f"请求失败: {type(payload).__name__}"

    return _classify_status(int(payload))


def _classify_status(code: int) -> tuple[Status, str]:
    if code == 429:
        return Status.RATE_LIMITED, "触发真实限流 (HTTP 429)"
    if code in (401, 403):
        return Status.RATE_LIMITED, f"被反爬 / 风控拦截 (HTTP {code})"
    if code in (500, 502, 503, 504):
        return Status.RATE_LIMITED, f"站点暂时不可用 (HTTP {code})"
    if 200 <= code < 400:
        return Status.UNKNOWN, f"响应正常 (HTTP {code}) 但规则未匹配，可能接口已改版"
    return Status.UNKNOWN, f"HTTP {code}，无法判定"


# 解析类异常 = 站点响应结构变了，Holehe 老代码抠不到预期字段
_PARSE_ERRORS = (IndexError, KeyError, ValueError, AttributeError, TypeError)


def _last_status(events: list[tuple[str, Any]]) -> int | None:
    for kind, payload in reversed(events):
        if kind == "status":
            return int(payload)
    return None


def _classify_exception(
    exc: Exception, events: list[tuple[str, Any]]
) -> tuple[Status, str]:
    """模块把异常抛到了外层（自身没兜住）时，据异常类型归类。"""
    if isinstance(exc, _NETWORK_ERRORS) or isinstance(exc, httpx.ConnectError):
        return Status.ERROR, "网络无法连通（境外站点通常需配置 SEEK_PROXY 代理）"
    if isinstance(exc, _PARSE_ERRORS):
        code = _last_status(events)
        suffix = f"（HTTP {code}）" if code is not None else ""
        return Status.UNKNOWN, f"接口响应已改版，解析失败{suffix}"
    if isinstance(exc, httpx.HTTPError):
        return Status.ERROR, f"请求失败: {type(exc).__name__}"
    return Status.ERROR, f"模块异常: {type(exc).__name__}: {exc}"

# Holehe 的子包名 -> seek 的分类
CATEGORY_MAP = {
    "social_media": "social",
    "mails": "mail",
    "music": "music",
    "medias": "media",
    "shopping": "shop",
    "products": "shop",
    "forum": "forum",
    "programing": "dev",
    "software": "dev",
    "productivity": "dev",
    "cms": "dev",
    "crm": "crm",
    "payment": "payment",
    "crowfunding": "crowdfunding",
    "porn": "adult",
    "osint": "osint",
    "learning": "edu",
    "jobs": "jobs",
    "medical": "medical",
    "sport": "sport",
    "transport": "transport",
    "real_estate": "realestate",
    "company": "other",
}


def holehe_available() -> bool:
    try:
        import holehe.core  # noqa: F401
    except Exception:
        return False
    return True


def _iter_module_funcs() -> Iterator[tuple[str, str, Callable]]:
    """复刻 Holehe 的 get_functions：模块路径超过 3 段者，取与文件同名的检测函数。"""
    from holehe.core import import_submodules

    modules = import_submodules("holehe.modules")
    for path, module in modules.items():
        parts = path.split(".")
        if len(parts) <= 3:
            continue
        site = parts[-1]
        func = module.__dict__.get(site)
        if callable(func) and asyncio.iscoroutinefunction(func):
            yield site, parts[2], func


class HoleheProvider(Provider):
    """包装单个 Holehe 模块。"""

    def __init__(self, func: Callable, info: ProviderInfo) -> None:
        super().__init__(info)
        self._func = func

    async def check(self, ctx: CheckContext) -> Result:
        out: list[dict[str, Any]] = []
        recorder = _RecordingClient(ctx.client)
        with Timer() as timer:
            try:
                await self._func(ctx.email, recorder, out)
            except asyncio.CancelledError:
                raise
            except Exception as exc:
                status, detail = _classify_exception(exc, recorder.events)
                return self.make_result(
                    status, elapsed_ms=timer.ms, detail=detail
                )

        if not out:
            return self.make_result(
                Status.UNKNOWN, elapsed_ms=timer.elapsed_ms, detail="模块无返回"
            )

        entry = out[0]
        data: dict[str, Any] = {}
        if entry.get("emailrecovery"):
            data["masked_email"] = entry["emailrecovery"]
        if entry.get("phoneNumber"):
            data["masked_phone"] = entry["phoneNumber"]
        if entry.get("others"):
            data["others"] = entry["others"]

        if entry.get("exists") is True:
            status, detail = Status.REGISTERED, "该邮箱已在此站点注册"
        elif entry.get("exists") is False and not entry.get("rateLimit"):
            status, detail = Status.NOT_REGISTERED, None
        else:
            # Holehe 的兜底（rateLimit=True 或 exists=None）—— 还原真实原因
            status, detail = _classify_failure(recorder.events)

        result = self.make_result(
            status, elapsed_ms=timer.elapsed_ms, detail=detail, data=data
        )
        domain = entry.get("domain")
        if domain:
            result.homepage = f"https://{domain}"
        return result


def load_holehe_providers() -> list[Provider]:
    if not holehe_available():
        log.info("未检测到 holehe，跳过其模块加载")
        return []

    providers: list[Provider] = []
    try:
        funcs = list(_iter_module_funcs())
    except Exception as exc:
        log.warning("加载 holehe 模块失败: %s", exc)
        return []

    for site, sub_pkg, func in funcs:
        info = ProviderInfo(
            name=f"holehe_{site}",
            title=site.replace("_", " ").title(),
            category=CATEGORY_MAP.get(sub_pkg, "other"),
            description=f"Holehe 模块 · {site}",
            notes="端点由 Holehe 维护，可能因站点改版而失效",
            kind="builtin",
        )
        providers.append(HoleheProvider(func, info))

    log.info("已从 holehe 加载 %d 个模块", len(providers))
    return providers
