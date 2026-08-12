from __future__ import annotations

import asyncio
import json
import logging
import time
from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles

from . import __version__
from .ai_agent import ai_configured, ai_settings, investigate_stream
from .config import Settings, get_settings
from .engine import Engine
from .models import ProviderInfo, ScanRequest, ScanResponse, ScanSummary
from .providers.registry import filter_providers, load_providers
from .ratelimit import SlidingWindowLimiter
from .utils import InvalidEmail, normalize_email, split_email

log = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    settings = get_settings()
    app.state.settings = settings
    app.state.providers = load_providers(settings)
    app.state.limiter = SlidingWindowLimiter(
        settings.rate_limit_scans, settings.rate_limit_window
    )
    log.info("已加载 %d 个检测模块", len(app.state.providers))
    yield


app = FastAPI(
    title="seek",
    description="邮箱注册痕迹反查框架",
    version=__version__,
    lifespan=lifespan,
)


def client_key(request: Request) -> str:
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


def guard(request: Request, email: str, consent: bool) -> str:
    """统一的入参校验 + 合规校验 + 限流。"""
    settings: Settings = request.app.state.settings

    try:
        normalized = normalize_email(email)
    except InvalidEmail as exc:
        raise HTTPException(status_code=422, detail=f"邮箱格式不正确: {exc}") from exc

    if settings.require_consent and not consent:
        raise HTTPException(status_code=403, detail="需要先确认授权声明才能发起查询")

    _local, domain = split_email(normalized)
    if not settings.is_domain_allowed(domain):
        raise HTTPException(
            status_code=403,
            detail=f"域名 {domain} 不在允许列表内（由 SEEK_ALLOWED_DOMAINS 配置）",
        )

    allowed, retry_after = request.app.state.limiter.check(client_key(request))
    if not allowed:
        raise HTTPException(
            status_code=429,
            detail=f"请求过于频繁，请 {retry_after} 秒后再试",
            headers={"Retry-After": str(retry_after)},
        )
    return normalized


def _split_csv(value: str | None) -> list[str]:
    return [part.strip() for part in (value or "").split(",") if part.strip()]


def providers_for(request: Request, profile: str | None) -> list:
    """按档位取模块列表：reliable 用启动时加载的白名单集合；full 懒加载全量+Holehe 并缓存。"""
    settings: Settings = request.app.state.settings
    resolved = settings.normalize_profile(profile, kind="scan")
    if resolved != "full":
        return request.app.state.providers

    cached = getattr(request.app.state, "providers_full", None)
    if cached is None:
        log.info("首次全网完整搜索：加载全量规则 + Holehe 模块…")
        cached = load_providers(settings, profile="full", include_holehe=True)
        request.app.state.providers_full = cached
        log.info("完整模式已加载 %d 个模块", len(cached))
    return cached


@app.get("/api/meta")
async def meta(request: Request) -> dict:
    settings: Settings = request.app.state.settings
    providers: list = request.app.state.providers
    return {
        "version": __version__,
        "require_consent": settings.require_consent,
        "allowed_domains": sorted(settings.domain_allowlist),
        "rate_limit": {
            "scans": settings.rate_limit_scans,
            "window": settings.rate_limit_window,
            "remaining": request.app.state.limiter.remaining(client_key(request)),
        },
        "provider_count": len(providers),
        "categories": sorted({p.info.category for p in providers}),
        "scan_profile": settings.normalize_profile(None, kind="scan"),
        "ai_profile": settings.normalize_profile(None, kind="ai"),
        "ai": {
            "configured": ai_configured(),
            "model": ai_settings()["model"] if ai_configured() else None,
            "base_url": ai_settings()["base_url"] if ai_configured() else None,
            "profile": settings.normalize_profile(None, kind="ai"),
        },
    }


@app.get("/api/providers", response_model=list[ProviderInfo])
async def providers(request: Request) -> list[ProviderInfo]:
    return [p.info for p in request.app.state.providers]


@app.post("/api/scan", response_model=ScanResponse)
async def scan(request: Request, payload: ScanRequest) -> ScanResponse:
    email = guard(request, payload.email, payload.consent)
    settings: Settings = request.app.state.settings
    providers = providers_for(request, payload.profile)
    async with Engine(providers, settings) as engine:
        return await engine.scan(email, payload.only, payload.exclude)


@app.get("/api/scan/stream")
async def scan_stream(
    request: Request,
    email: str = Query(..., description="要查询的邮箱"),
    consent: bool = Query(False, description="是否已确认授权声明"),
    only: str | None = Query(None, description="仅运行这些模块/分类，逗号分隔"),
    exclude: str | None = Query(None, description="排除这些模块/分类，逗号分隔"),
    profile: str | None = Query(None, description="档位：reliable（默认）或 full（全网完整搜索）"),
) -> StreamingResponse:
    settings: Settings = request.app.state.settings
    only_list, exclude_list = _split_csv(only), _split_csv(exclude)
    providers = providers_for(request, profile)

    # EventSource 读不到 HTTP 错误响应体，所以校验失败也走事件下发
    try:
        normalized = guard(request, email, consent)
    except HTTPException as exc:
        return _sse_error_response(str(exc.detail))

    async def event_stream() -> AsyncIterator[str]:
        started = time.perf_counter()
        results = []
        try:
            async with Engine(providers, settings) as engine:
                total = len(filter_providers(engine.providers, only_list, exclude_list))
                yield _sse("start", {"email": normalized, "total": total})
                async for result in engine.stream(normalized, only_list, exclude_list):
                    if await request.is_disconnected():
                        log.info("客户端断开，终止扫描")
                        return
                    results.append(result)
                    yield _sse("result", result.model_dump(mode="json"))
            elapsed = int((time.perf_counter() - started) * 1000)
            summary = ScanSummary.from_results(normalized, results, elapsed)
            yield _sse("summary", summary.model_dump(mode="json"))
        except asyncio.CancelledError:
            raise
        except Exception as exc:
            log.exception("扫描过程出错")
            yield _sse("error", {"message": f"{type(exc).__name__}: {exc}"})

    return StreamingResponse(
        event_stream(), media_type="text/event-stream", headers=SSE_HEADERS
    )


@app.get("/api/ai/investigate")
async def ai_investigate(
    request: Request,
    email: str = Query(..., description="要调查的邮箱"),
    consent: bool = Query(False, description="是否已确认授权声明"),
) -> StreamingResponse:
    """AI 智能体：用大模型 API Key 调度扫描 + 公开搜索，汇总可能注册的站点。"""
    if not ai_configured():
        return _sse_error_response(
            "未配置 AI API Key。请在 .env 设置 SEEK_AI_API_KEY（兼容 OpenAI / DeepSeek 等）"
        )
    try:
        normalized = guard(request, email, consent)
    except HTTPException as exc:
        return _sse_error_response(str(exc.detail))

    settings: Settings = request.app.state.settings

    async def event_stream() -> AsyncIterator[str]:
        try:
            async for chunk in investigate_stream(
                normalized, request.app.state.providers, settings
            ):
                if await request.is_disconnected():
                    return
                yield chunk
        except asyncio.CancelledError:
            raise
        except Exception as exc:
            log.exception("AI 调查流出错")
            yield _sse("error", {"message": f"{type(exc).__name__}: {exc}"})

    return StreamingResponse(
        event_stream(), media_type="text/event-stream", headers=SSE_HEADERS
    )


def _sse(event: str, data: dict) -> str:
    return f"event: {event}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"


SSE_HEADERS = {
    "Cache-Control": "no-cache",
    "Connection": "keep-alive",
    "X-Accel-Buffering": "no",
}


def _sse_error_response(message: str) -> StreamingResponse:
    async def one_shot() -> AsyncIterator[str]:
        yield _sse("error", {"message": message})

    return StreamingResponse(one_shot(), media_type="text/event-stream", headers=SSE_HEADERS)


# ---------- 静态前端 ----------
_settings = get_settings()
if _settings.web_dir.exists():
    app.mount("/static", StaticFiles(directory=_settings.web_dir), name="static")

    @app.get("/", include_in_schema=False)
    async def index() -> FileResponse:
        return FileResponse(_settings.web_dir / "index.html")


@app.exception_handler(InvalidEmail)
async def invalid_email_handler(_request: Request, exc: InvalidEmail) -> JSONResponse:
    return JSONResponse(status_code=422, content={"detail": str(exc)})
