"""离线测试：用假的 HTTP 传输层验证规则引擎，不产生任何真实外部请求。

直接运行：python tests/test_engine.py
或使用 pytest：pytest tests/
"""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

import httpx

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from seek.engine import Engine  # noqa: E402
from seek.models import Status  # noqa: E402
from seek.providers.declarative import DeclarativeProvider, build_provider_info  # noqa: E402
from seek.utils import build_context, json_path, normalize_email, render  # noqa: E402

EMAIL = "alice@example.com"


def make_provider(spec: dict) -> DeclarativeProvider:
    return DeclarativeProvider(build_provider_info(spec, spec["name"]), spec)


SPEC = {
    "name": "fake_site",
    "title": "假站点",
    "category": "social",
    "request": {
        "method": "POST",
        "url": "https://fake.test/api/exists",
        "json": {"email": "{email}", "hash": "{email_sha256}"},
    },
    "rules": [
        {
            "registered_if": {"status_in": [200], "json_path_truthy": "data.exists"},
            "detail": "已注册",
        },
        {"not_registered_if": {"status_in": [200, 404]}, "detail": "未注册"},
        {"rate_limited_if": {"status_in": [429]}},
        {"error_if": {"status_in": [403]}, "detail": "被风控"},
    ],
    "extract": {"masked_phone": "data.phone", "linked": "data.accounts[].name"},
    "default": "unknown",
}


def run_with(handler) -> list:
    return run_with_spec(SPEC, handler)


def run_with_spec(spec: dict, handler) -> list:
    provider = make_provider(spec)

    async def go():
        transport = httpx.MockTransport(handler)
        async with Engine([provider], transport=transport) as engine:
            return await engine.scan(EMAIL)

    return asyncio.run(go()).results


def test_registered_and_extract():
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.method == "POST"
        assert b'"alice@example.com"' in request.content
        return httpx.Response(
            200,
            json={
                "data": {
                    "exists": True,
                    "phone": "+86 138****8888",
                    "accounts": [{"name": "twitter"}, {"name": "github"}],
                }
            },
        )

    result = run_with(handler)[0]
    assert result.status is Status.REGISTERED, result
    assert result.detail == "已注册"
    assert result.data["masked_phone"] == "+86 138****8888"
    assert result.data["linked"] == ["twitter", "github"]
    print("[ok] 已注册判定 + 字段提取")


def test_not_registered():
    result = run_with(lambda r: httpx.Response(200, json={"data": {"exists": False}}))[0]
    assert result.status is Status.NOT_REGISTERED, result
    print("[ok] 未注册判定")


def test_rate_limited_and_error():
    assert run_with(lambda r: httpx.Response(429))[0].status is Status.RATE_LIMITED
    assert run_with(lambda r: httpx.Response(403))[0].status is Status.ERROR
    print("[ok] 限流 / 风控判定")


def test_unknown_fallback():
    result = run_with(lambda r: httpx.Response(500, text="boom"))[0]
    assert result.status is Status.UNKNOWN, result
    assert result.http_status == 500
    print("[ok] 兜底 unknown")


def test_network_error_is_isolated():
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("dns fail", request=request)

    result = run_with(handler)[0]
    assert result.status is Status.ERROR
    assert "网络错误" in (result.detail or "")
    print("[ok] 网络异常被隔离")


def test_missing_requirement_is_skipped():
    spec = dict(SPEC, name="needs_key", requires=["DEFINITELY_NOT_SET_KEY_XYZ"])
    spec["request"] = dict(SPEC["request"], url="https://fake.test/{env.DEFINITELY_NOT_SET_KEY_XYZ}")
    provider = make_provider(spec)
    assert provider.info.ready is False

    async def go():
        async with Engine([provider], transport=httpx.MockTransport(lambda r: httpx.Response(200))) as e:
            return await e.scan(EMAIL)

    result = asyncio.run(go()).results[0]
    assert result.status is Status.SKIPPED, result
    print("[ok] 缺少 API Key 自动跳过")


def test_summary_counts():
    specs = [
        dict(SPEC, name=f"site{i}", rules=[{"registered_if": {"status_in": [200]}}])
        for i in range(5)
    ]
    providers = [make_provider(s) for s in specs]

    async def go():
        transport = httpx.MockTransport(lambda r: httpx.Response(200, json={}))
        async with Engine(providers, transport=transport) as engine:
            return await engine.scan(EMAIL)

    response = asyncio.run(go())
    assert response.summary.total == 5
    assert response.summary.registered == 5
    print("[ok] 并发调度与汇总统计")


def test_template_and_jsonpath():
    ctx = build_context(EMAIL)
    assert render("{local}@{domain}", ctx) == EMAIL
    assert len(ctx["email_sha256"]) == 64
    assert render("{email_urlenc}", ctx) == "alice%40example.com"

    data = {"entry": [{"accounts": [{"shortname": "gh"}, {"shortname": "tw"}]}]}
    assert json_path(data, "entry.0.accounts[].shortname") == ["gh", "tw"]
    assert json_path([{"Name": "A"}, {"Name": "B"}], "[].Name") == ["A", "B"]
    assert json_path(data, "entry.0.missing") is None

    assert normalize_email("  Alice@Example.COM ") == "Alice@example.com"
    print("[ok] 模板变量 / JSON 路径 / 邮箱归一化")


def test_prepare_multistep_with_csrf():
    """验证两步请求：先从 cookie 取 CSRF token，再带着它 POST 查重。"""
    spec = {
        "name": "csrf_site",
        "title": "需要 CSRF 的站点",
        "category": "social",
        "prepare": [
            {
                "method": "GET",
                "url": "https://csrf.test/signup",
                "save": {"token": {"from": "cookie", "name": "csrftoken"}},
            }
        ],
        "request": {
            "method": "POST",
            "url": "https://csrf.test/api/check",
            "headers": {"X-CSRFToken": "{token}"},
            "data": {"email": "{email}"},
        },
        "rules": [{"registered_if": {"json_path_truthy": "taken"}, "detail": "已注册"}],
        "default": "not_registered",
    }
    seen = {}

    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/signup":
            return httpx.Response(200, headers={"set-cookie": "csrftoken=SECRET123; Path=/"})
        seen["csrf_header"] = request.headers.get("x-csrftoken")
        seen["sent_cookie"] = request.headers.get("cookie")
        return httpx.Response(200, json={"taken": True})

    result = run_with_spec(spec, handler)[0]
    assert result.status is Status.REGISTERED, result
    assert seen["csrf_header"] == "SECRET123", seen
    assert "csrftoken=SECRET123" in (seen.get("sent_cookie") or ""), seen
    print("[ok] 两步请求 + CSRF token 透传 + cookie 自动携带")


def test_prepare_missing_required_token():
    spec = {
        "name": "csrf_fail",
        "title": "取不到 token",
        "category": "social",
        "prepare": [
            {
                "method": "GET",
                "url": "https://csrf.test/signup",
                "save": {"token": {"from": "cookie", "name": "csrftoken"}},
            }
        ],
        "request": {"method": "GET", "url": "https://csrf.test/check?t={token}"},
        "rules": [],
    }
    result = run_with_spec(spec, lambda r: httpx.Response(200))[0]
    assert result.status is Status.ERROR
    assert "token" in (result.detail or "")
    print("[ok] 预备请求取不到必需变量 -> error")


def test_definitions_all_parse():
    from seek.providers.registry import load_providers

    providers = load_providers(profile="full", include_holehe=False)
    assert len(providers) >= 50, f"模块过少: {len(providers)}"
    names = {p.info.name for p in providers}
    assert "example_site" not in names
    assert not any(n.startswith("holehe_") for n in names)
    print(f"[ok] 规则文件全部解析通过（共 {len(providers)} 个模块）")


if __name__ == "__main__":
    failures = 0
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            try:
                fn()
            except AssertionError as exc:
                failures += 1
                print(f"[FAIL] {name}: {exc}")
    print("\n全部通过" if not failures else f"\n{failures} 项失败")
    sys.exit(1 if failures else 0)
