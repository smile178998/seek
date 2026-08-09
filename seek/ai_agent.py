"""AI OSINT：先跑齐所有同类工具，再用大模型 API Key 汇总成报告。

流程：
  1. aggregators.run_all_backends  — seek 规则 + Holehe + Gravatar + 网页搜索 + socialscan
  2. 把证据交给大模型
  3. 模型调用 submit_report 输出「已确认 / 疑似」清单

兼容 OpenAI / DeepSeek / Moonshot / OpenRouter 等 OpenAI 风格接口。
"""

from __future__ import annotations

import asyncio
import json
import logging
import re
from typing import Any, AsyncIterator, Awaitable, Callable
from urllib.parse import quote_plus, urlparse

import httpx

from .aggregators import bundle_for_llm, enrich_report, run_all_backends
from .config import Settings, build_ssl_verify, lookup_secret
from .providers.base import Provider
from .utils import mask_email

log = logging.getLogger(__name__)

EventSink = Callable[[str, dict[str, Any]], Awaitable[None] | None]

SYSTEM_PROMPT = """你是邮箱 OSINT 汇总助手。系统已按「可靠模式」或「完整模式」跑完检测工具，
下面会给你证据 JSON（含 stats）。

你的任务：
1. 只根据证据归纳，禁止编造未出现的站点。
2. summary 必须先写清有效判定数字：已注册 / 未注册 / 情报；不要把「已注册为空」说成工具失效。
3. confirmed：工具明确判定 registered，或 Gravatar 明确有资料。
4. intel：域名 MX、邮箱服务商、一次性邮箱等情报（必须写入，不要丢弃）。
5. not_registered：工具明确判定未注册的站点（可列代表性若干条）。
6. likely：网页搜索强相关、Gravatar 关联社交账号等疑似线索。
7. unchecked_or_failed：失败/限流/无法判定（不要当成未注册）。
8. 用简体中文写 summary 和 next_steps。
9. 必须调用 submit_report，不要只输出散文。
"""

TOOLS: list[dict[str, Any]] = [
    {
        "type": "function",
        "function": {
            "name": "fetch_url",
            "description": "可选：抓取某条网页搜索结果的公开页面做核对",
            "parameters": {
                "type": "object",
                "properties": {"url": {"type": "string"}},
                "required": ["url"],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "submit_report",
            "description": "提交最终结构化报告",
            "parameters": {
                "type": "object",
                "properties": {
                    "summary": {"type": "string"},
                    "confirmed": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "site": {"type": "string"},
                                "evidence": {"type": "string"},
                                "url": {"type": "string"},
                                "source": {"type": "string"},
                            },
                            "required": ["site", "evidence"],
                        },
                    },
                    "intel": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "site": {"type": "string"},
                                "evidence": {"type": "string"},
                                "url": {"type": "string"},
                                "source": {"type": "string"},
                            },
                            "required": ["site", "evidence"],
                        },
                    },
                    "not_registered": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "site": {"type": "string"},
                                "evidence": {"type": "string"},
                                "url": {"type": "string"},
                                "source": {"type": "string"},
                            },
                            "required": ["site", "evidence"],
                        },
                    },
                    "likely": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "site": {"type": "string"},
                                "evidence": {"type": "string"},
                                "url": {"type": "string"},
                                "source": {"type": "string"},
                            },
                            "required": ["site", "evidence"],
                        },
                    },
                    "unchecked_or_failed": {
                        "type": "array",
                        "items": {"type": "string"},
                    },
                    "next_steps": {
                        "type": "array",
                        "items": {"type": "string"},
                    },
                },
                "required": ["summary", "confirmed", "likely", "intel", "not_registered"],
                "additionalProperties": False,
            },
        },
    },
]


def ai_configured() -> bool:
    return bool(lookup_secret("AI_API_KEY") or lookup_secret("OPENAI_API_KEY"))


def ai_settings() -> dict[str, str]:
    key = lookup_secret("AI_API_KEY") or lookup_secret("OPENAI_API_KEY") or ""
    base = (
        lookup_secret("AI_BASE_URL")
        or lookup_secret("OPENAI_BASE_URL")
        or "https://api.openai.com/v1"
    ).rstrip("/")
    model = lookup_secret("AI_MODEL") or "gpt-4o-mini"
    return {"api_key": key, "base_url": base, "model": model}


class AIInvestigator:
    def __init__(
        self,
        email: str,
        providers: list[Provider],
        settings: Settings,
        emit: EventSink | None = None,
    ) -> None:
        self.email = email
        self.providers = providers  # 保留兼容；实际全量跑 aggregators
        self.settings = settings
        self.emit = emit
        self._report: dict[str, Any] | None = None
        self._bundle: dict[str, Any] | None = None

    async def _emit(self, event: str, data: dict[str, Any]) -> None:
        if not self.emit:
            return
        result = self.emit(event, data)
        if hasattr(result, "__await__"):
            await result  # type: ignore[misc]

    async def run(self, max_rounds: int = 6) -> dict[str, Any]:
        cfg = ai_settings()
        if not cfg["api_key"]:
            raise RuntimeError(
                "未配置 AI API Key。请在 .env 设置 SEEK_AI_API_KEY（或 OPENAI_API_KEY）"
            )

        profile = self.settings.normalize_profile(None, kind="ai")
        await self._emit("ai_start", {
            "email": self.email,
            "model": cfg["model"],
            "base_url": cfg["base_url"],
            "mode": "aggregate_then_summarize",
            "profile": profile,
        })

        # ---------- 第一步：按档位跑检测工具 ----------
        self._bundle = await run_all_backends(
            self.email, self.settings, emit=self.emit, profile=profile,
        )
        evidence = bundle_for_llm(self._bundle)

        messages: list[dict[str, Any]] = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": (
                    f"目标邮箱：{self.email}（展示 {mask_email(self.email)}）\n"
                    f"下列 JSON 是已跑完的多工具聚合证据，请据此 submit_report：\n\n{evidence}"
                ),
            },
        ]

        async with httpx.AsyncClient(
            timeout=90.0,
            verify=build_ssl_verify(self.settings),
            proxy=self.settings.proxy or None,
        ) as http:
            for round_i in range(max_rounds):
                await self._emit("ai_thinking", {"round": round_i + 1, "max": max_rounds})
                response = await self._chat(http, cfg, messages)
                choice = response["choices"][0]["message"]
                messages.append(choice)

                tool_calls = choice.get("tool_calls") or []
                if not tool_calls:
                    messages.append({
                        "role": "user",
                        "content": "请立刻调用 submit_report，不要只输出文字。",
                    })
                    continue

                for call in tool_calls:
                    name = call["function"]["name"]
                    raw_args = call["function"].get("arguments") or "{}"
                    try:
                        args = json.loads(raw_args) if isinstance(raw_args, str) else raw_args
                    except json.JSONDecodeError:
                        args = {}

                    await self._emit("ai_tool", {"name": name, "args": args})
                    result = await self._dispatch(name, args, http)
                    await self._emit("ai_tool_result", {"name": name, "preview": _preview(result)})
                    messages.append({
                        "role": "tool",
                        "tool_call_id": call["id"],
                        "content": json.dumps(result, ensure_ascii=False)[:12000],
                    })
                    if name == "submit_report" and self._report is not None:
                        await self._emit("ai_report", self._report)
                        return self._report

            fallback = self._fallback_report()
            await self._emit("ai_report", fallback)
            return fallback

    async def _chat(
        self, http: httpx.AsyncClient, cfg: dict[str, str], messages: list[dict]
    ) -> dict[str, Any]:
        url = f"{cfg['base_url']}/chat/completions"
        payload = {
            "model": cfg["model"],
            "messages": messages,
            "tools": TOOLS,
            "tool_choice": "auto",
            "temperature": 0.2,
        }
        resp = await http.post(
            url,
            headers={
                "Authorization": f"Bearer {cfg['api_key']}",
                "Content-Type": "application/json",
            },
            json=payload,
        )
        if resp.status_code >= 400:
            raise RuntimeError(f"AI API 错误 HTTP {resp.status_code}: {resp.text[:400]}")
        return resp.json()

    async def _dispatch(
        self, name: str, args: dict[str, Any], http: httpx.AsyncClient
    ) -> Any:
        if name == "fetch_url":
            return await _fetch_snippet(http, str(args.get("url") or ""))

        if name == "submit_report":
            raw = {
                "email": self.email,
                "summary": args.get("summary") or "",
                "confirmed": args.get("confirmed") or [],
                "likely": args.get("likely") or [],
                "intel": args.get("intel") or [],
                "not_registered": args.get("not_registered") or [],
                "unchecked_or_failed": args.get("unchecked_or_failed") or [],
                "next_steps": args.get("next_steps") or [],
            }
            self._report = enrich_report(raw, self._bundle or {})
            return {"ok": True}

        return {"error": f"未知工具: {name}"}

    def _fallback_report(self) -> dict[str, Any]:
        bundle = self._bundle or {}
        likely = []
        g = (bundle.get("backends") or {}).get("gravatar") or {}
        if g.get("profile") and g["profile"].get("accounts"):
            for acc in g["profile"]["accounts"]:
                likely.append({
                    "site": str(acc),
                    "evidence": "Gravatar 资料中关联的账号",
                    "source": "gravatar",
                })
        for hit in ((bundle.get("backends") or {}).get("web_search") or {}).get("results") or [][:8]:
            likely.append({
                "site": hit.get("title") or hit.get("url"),
                "evidence": hit.get("snippet") or "公开网页搜索命中",
                "url": hit.get("url") or "",
                "source": "web_search",
            })
        return enrich_report({
            "email": self.email,
            "summary": "AI 未按时提交报告，已根据可靠检测结果自动汇总。",
            "confirmed": [],
            "likely": likely,
            "intel": [],
            "not_registered": [],
            "unchecked_or_failed": [],
            "next_steps": [],
        }, bundle)


def _preview(result: Any, limit: int = 280) -> str:
    text = json.dumps(result, ensure_ascii=False) if not isinstance(result, str) else result
    return text if len(text) <= limit else text[:limit] + "…"


async def _fetch_snippet(http: httpx.AsyncClient, url: str) -> dict[str, Any]:
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https") or not parsed.netloc:
        return {"error": "非法 URL"}
    try:
        resp = await http.get(
            url,
            headers={"User-Agent": "Mozilla/5.0 (compatible; seek-osint/0.1)"},
            follow_redirects=True,
            timeout=15.0,
        )
    except httpx.HTTPError as exc:
        return {"error": str(exc)}
    text = re.sub(r"(?is)<script.*?>.*?</script>", " ", resp.text)
    text = re.sub(r"(?is)<style.*?>.*?</style>", " ", text)
    text = re.sub(r"(?s)<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return {"url": str(resp.url), "status": resp.status_code, "text": text[:3000]}


async def investigate_stream(
    email: str,
    providers: list[Provider],
    settings: Settings,
) -> AsyncIterator[str]:
    queue: asyncio.Queue[tuple[str, dict] | None] = asyncio.Queue()

    async def emit(event: str, data: dict) -> None:
        await queue.put((event, data))

    async def runner() -> None:
        try:
            agent = AIInvestigator(email, providers, settings, emit=emit)
            await agent.run()
        except Exception as exc:
            log.exception("AI 调查失败")
            await queue.put(("error", {"message": f"{type(exc).__name__}: {exc}"}))
        finally:
            await queue.put(None)

    task = asyncio.create_task(runner())
    try:
        while True:
            item = await queue.get()
            if item is None:
                break
            event, data = item
            yield f"event: {event}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"
    finally:
        if not task.done():
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
