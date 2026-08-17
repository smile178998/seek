from __future__ import annotations

import asyncio
import ipaddress
import json
import logging
import time
from contextlib import asynccontextmanager
from typing import AsyncIterator
from urllib.parse import urlparse

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from starlette.datastructures import MutableHeaders
from starlette.middleware.httpsredirect import HTTPSRedirectMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware

from . import __version__
from .ai_agent import ai_configured, ai_settings, investigate_stream
from .config import Settings, get_settings
from .engine import Engine
from .models import (
    AIInvestigateRequest,
    ProviderInfo,
    ScanRequest,
    ScanResponse,
    ScanSummary,
)
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


_settings = get_settings()

app = FastAPI(
    title="seek",
    description="邮箱注册痕迹反查框架",
    version=__version__,
    lifespan=lifespan,
    docs_url="/docs" if _settings.docs_enabled else None,
    redoc_url="/redoc" if _settings.docs_enabled else None,
    openapi_url="/openapi.json" if _settings.docs_enabled else None,
)


class SecurityHeadersMiddleware:
    """Apply browser hardening without buffering streaming responses."""

    def __init__(self, app, settings: Settings) -> None:
        self.app = app
        self.settings = settings

    async def __call__(self, scope, receive, send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        header_map = {key.lower(): value for key, value in scope.get("headers", [])}
        try:
            content_length = int(header_map.get(b"content-length", b"0"))
        except ValueError:
            content_length = self.settings.max_request_bytes + 1
        chunked_body = (
            b"transfer-encoding" in header_map and b"content-length" not in header_map
        )
        if chunked_body or content_length > self.settings.max_request_bytes:
            response = JSONResponse({"detail": "Request body too large"}, status_code=413)
            await response(scope, receive, send)
            return

        async def secure_send(message) -> None:
            if message["type"] == "http.response.start":
                headers = MutableHeaders(scope=message)
                headers["Content-Security-Policy"] = (
                    "default-src 'self'; script-src 'self'; "
                    "style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; "
                    "connect-src 'self'; font-src 'self'; object-src 'none'; "
                    "base-uri 'none'; frame-ancestors 'none'; form-action 'self'"
                )
                headers["X-Content-Type-Options"] = "nosniff"
                headers["X-Frame-Options"] = "DENY"
                headers["Referrer-Policy"] = "no-referrer"
                headers["Permissions-Policy"] = (
                    "camera=(), microphone=(), geolocation=(), payment=(), usb=()"
                )
                headers["Cross-Origin-Opener-Policy"] = "same-origin"
                headers["Cross-Origin-Resource-Policy"] = "same-origin"
                headers["X-Permitted-Cross-Domain-Policies"] = "none"
                headers["X-Robots-Tag"] = "noindex, nofollow, noarchive"
                if scope.get("path", "").startswith("/api/"):
                    headers["Cache-Control"] = "no-store"
                if self.settings.hsts_enabled:
                    headers["Strict-Transport-Security"] = (
                        "max-age=31536000; includeSubDomains"
                    )
            await send(message)

        await self.app(scope, receive, secure_send)


app.add_middleware(TrustedHostMiddleware, allowed_hosts=_settings.host_allowlist)
if _settings.force_https:
    app.add_middleware(HTTPSRedirectMiddleware)
app.add_middleware(SecurityHeadersMiddleware, settings=_settings)


def client_key(request: Request) -> str:
    peer = request.client.host if request.client else None
    settings: Settings = request.app.state.settings
    if settings.is_trusted_proxy(peer):
        forwarded = request.headers.get("x-forwarded-for")
        if forwarded:
            candidate = forwarded.split(",", 1)[0].strip()
            try:
                return ipaddress.ip_address(candidate).compressed
            except ValueError:
                pass
    return peer or "unknown"


def _enforce_same_origin(request: Request) -> None:
    if request.headers.get("sec-fetch-site", "").lower() == "cross-site":
        raise HTTPException(status_code=403, detail="Cross-site requests are not allowed")
    origin = request.headers.get("origin")
    if not origin:
        return
    parsed = urlparse(origin)
    expected_host = request.headers.get("host", "").lower()
    if parsed.scheme not in {"http", "https"} or parsed.netloc.lower() != expected_host:
        raise HTTPException(status_code=403, detail="Origin is not allowed")


def guard(request: Request, email: str, consent: bool) -> str:
    """统一的入参校验 + 合规校验 + 限流。"""
    settings: Settings = request.app.state.settings

    try:
        normalized = normalize_email(email)
    except InvalidEmail as exc:
        raise HTTPException(status_code=422, detail=f"邮箱格式不正确: {exc}") from exc

    if settings.require_consent and not consent:
        raise HTTPException(status_code=403, detail="需要先确认授权声明才能发起查询")

    domain = split_email(normalized)[1]
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


def _validate_selection(values: list[str]) -> list[str]:
    if len(values) > 100 or any(len(value) > 64 for value in values):
        raise HTTPException(status_code=422, detail="Too many or invalid provider filters")
    return values


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
            "profile": settings.normalize_profile(None, kind="ai"),
        },
    }


@app.get("/api/providers", response_model=list[ProviderInfo])
async def providers(
    request: Request,
    profile: str | None = Query(None, description="档位：reliable 或 full"),
) -> list[ProviderInfo]:
    return [p.info for p in providers_for(request, profile)]


@app.post("/api/scan", response_model=ScanResponse)
async def scan(request: Request, payload: ScanRequest) -> ScanResponse:
    email = guard(request, payload.email, payload.consent)
    only = _validate_selection(payload.only)
    exclude = _validate_selection(payload.exclude)
    settings: Settings = request.app.state.settings
    providers = providers_for(request, payload.profile)
    async with Engine(providers, settings) as engine:
        return await engine.scan(email, only, exclude)


async def _scan_stream_impl(
    request: Request,
    email: str,
    consent: bool,
    only_list: list[str],
    exclude_list: list[str],
    profile: str | None,
) -> StreamingResponse:
    settings: Settings = request.app.state.settings
    _enforce_same_origin(request)
    resolved_profile = settings.normalize_profile(profile, kind="scan")
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
                yield _sse(
                    "start",
                    {"email": normalized, "total": total, "profile": resolved_profile},
                )
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
            yield _sse("error", {"message": "Operation failed; please try again later"})

    return StreamingResponse(
        event_stream(), media_type="text/event-stream", headers=SSE_HEADERS
    )


@app.post("/api/scan/stream")
async def scan_stream(request: Request, payload: ScanRequest) -> StreamingResponse:
    _validate_selection(payload.only)
    _validate_selection(payload.exclude)
    return await _scan_stream_impl(
        request,
        email=payload.email,
        consent=payload.consent,
        only_list=payload.only,
        exclude_list=payload.exclude,
        profile=payload.profile,
    )


async def _ai_investigate_impl(
    request: Request,
    email: str,
    consent: bool,
    lang: str,
) -> StreamingResponse:
    """AI 智能体：用大模型 API Key 调度扫描 + 公开搜索，汇总可能注册的站点。"""
    _enforce_same_origin(request)
    if not ai_configured():
        return _sse_error_response(
            "未配置 AI API Key。请在 .env 设置 SEEK_AI_API_KEY（兼容 OpenAI / DeepSeek 等）"
        )
    try:
        normalized = guard(request, email, consent)
    except HTTPException as exc:
        return _sse_error_response(str(exc.detail))

    settings: Settings = request.app.state.settings
    language = "en" if lang.lower() == "en" else "zh"

    async def event_stream() -> AsyncIterator[str]:
        try:
            async for chunk in investigate_stream(
                normalized, request.app.state.providers, settings, language=language
            ):
                if await request.is_disconnected():
                    return
                yield chunk
        except asyncio.CancelledError:
            raise
        except Exception as exc:
            log.exception("AI 调查流出错")
            yield _sse("error", {"message": "Operation failed; please try again later"})

    return StreamingResponse(
        event_stream(), media_type="text/event-stream", headers=SSE_HEADERS
    )


@app.post("/api/ai/investigate")
async def ai_investigate(
    request: Request, payload: AIInvestigateRequest
) -> StreamingResponse:
    return await _ai_investigate_impl(
        request,
        email=payload.email,
        consent=payload.consent,
        lang=payload.lang,
    )


def _sse(event: str, data: dict) -> str:
    return f"event: {event}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"


SSE_HEADERS = {
    "Cache-Control": "no-store",
    "Connection": "keep-alive",
    "X-Accel-Buffering": "no",
}


def _sse_error_response(message: str) -> StreamingResponse:
    async def one_shot() -> AsyncIterator[str]:
        yield _sse("error", {"message": message})

    return StreamingResponse(one_shot(), media_type="text/event-stream", headers=SSE_HEADERS)


# ---------- 静态前端 ----------
if _settings.web_dir.exists():
    app.mount("/static", StaticFiles(directory=_settings.web_dir), name="static")

    @app.get("/", include_in_schema=False)
    async def index() -> FileResponse:
        return FileResponse(_settings.web_dir / "index.html")
