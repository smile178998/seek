from __future__ import annotations

import asyncio
import sys
from pathlib import Path
from types import SimpleNamespace

from fastapi import FastAPI
from fastapi.testclient import TestClient
from starlette.requests import Request

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from seek.ai_agent import _validate_public_url  # noqa: E402
from seek.api import (  # noqa: E402
    SecurityHeadersMiddleware,
    _enforce_same_origin,
    app,
    client_key,
)
from seek.config import Settings  # noqa: E402
from seek.ratelimit import SlidingWindowLimiter  # noqa: E402


def make_request(settings: Settings, peer: str, forwarded: str | None = None) -> Request:
    headers = [(b"host", b"localhost")]
    if forwarded:
        headers.append((b"x-forwarded-for", forwarded.encode("ascii")))
    fake_app = SimpleNamespace(state=SimpleNamespace(settings=settings))
    return Request(
        {
            "type": "http",
            "method": "GET",
            "path": "/api/meta",
            "headers": headers,
            "client": (peer, 12345),
            "server": ("localhost", 80),
            "scheme": "http",
            "app": fake_app,
        }
    )


def test_forwarded_ip_is_ignored_by_default() -> None:
    request = make_request(Settings(trust_proxy_headers=False), "203.0.113.7", "1.2.3.4")
    assert client_key(request) == "203.0.113.7"


def test_forwarded_ip_requires_a_trusted_proxy() -> None:
    settings = Settings(
        trust_proxy_headers=True,
        trusted_proxies="10.0.0.0/8",
    )
    assert client_key(make_request(settings, "198.51.100.8", "1.2.3.4")) == "198.51.100.8"
    assert client_key(make_request(settings, "10.0.0.8", "1.2.3.4")) == "1.2.3.4"


def test_cross_site_browser_request_is_rejected() -> None:
    request = make_request(Settings(), "127.0.0.1")
    request.scope["headers"].append((b"origin", b"https://evil.example"))
    try:
        _enforce_same_origin(request)
    except Exception as exc:
        assert getattr(exc, "status_code", None) == 403
    else:
        raise AssertionError("cross-site origin was accepted")


def test_rate_limiter_has_a_bounded_key_store() -> None:
    limiter = SlidingWindowLimiter(limit=1, window_seconds=600, max_keys=3)
    for index in range(20):
        limiter.check(f"client-{index}")
    assert len(limiter._hits) <= 3


def test_ssrf_validator_blocks_non_public_destinations() -> None:
    blocked = [
        "http://127.0.0.1/",
        "http://169.254.169.254/latest/meta-data/",
        "http://[::1]/",
        "https://user:pass@example.com/",
        "https://93.184.216.34:8443/",
    ]
    for url in blocked:
        allowed, _ = asyncio.run(_validate_public_url(url))
        assert not allowed, url
    allowed, _ = asyncio.run(_validate_public_url("https://93.184.216.34/"))
    assert allowed


def test_security_headers_and_request_limit() -> None:
    inner = FastAPI()

    @inner.get("/")
    async def home() -> dict[str, bool]:
        return {"ok": True}

    protected = SecurityHeadersMiddleware(inner, Settings(max_request_bytes=16))
    with TestClient(protected) as client:
        response = client.get("/")
        assert response.headers["x-content-type-options"] == "nosniff"
        assert response.headers["x-frame-options"] == "DENY"
        assert "frame-ancestors 'none'" in response.headers["content-security-policy"]
        rejected = client.post("/", content=b"x" * 17)
        assert rejected.status_code == 413


def test_sensitive_stream_endpoints_are_post_only() -> None:
    methods = {
        route.path: route.methods
        for route in app.routes
        if route.path in {"/api/scan/stream", "/api/ai/investigate"}
    }
    assert methods["/api/scan/stream"] == {"POST"}
    assert methods["/api/ai/investigate"] == {"POST"}


def test_phone_stream_returns_structured_validation_error() -> None:
    with TestClient(app, base_url="http://localhost") as client:
        response = client.post(
            "/api/phone-scan/stream",
            json={"phone": "+31 (0)20", "consent": True},
        )
    assert response.status_code == 200
    assert '"code": "invalid_phone"' in response.text
    assert "Invalid phone number:" in response.text
