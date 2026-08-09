from __future__ import annotations

import json
import re
from typing import Any

import httpx

from ..config import lookup_secret
from ..models import ProviderInfo, Result, Status
from ..utils import TemplateError, build_context, json_path, render, render_any
from .base import CheckContext, Provider, Timer

# 规则条件 -> 命中后判定的状态
_CONDITION_TO_STATUS = {
    "registered_if": Status.REGISTERED,
    "not_registered_if": Status.NOT_REGISTERED,
    "info_if": Status.INFO,
    "unknown_if": Status.UNKNOWN,
    "rate_limited_if": Status.RATE_LIMITED,
    "error_if": Status.ERROR,
}


class RuleConfigError(ValueError):
    pass


class PrepareError(RuntimeError):
    """预备请求阶段出错（拿不到 token、网络失败等）。"""


def _as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    return value if isinstance(value, list) else [value]


class DeclarativeProvider(Provider):
    """由 YAML 定义驱动的通用检测模块。

    定义文件结构示例见 seek/definitions/*.yaml 与 README。
    """

    def __init__(self, info: ProviderInfo, spec: dict[str, Any]) -> None:
        super().__init__(info)
        self.spec = spec
        self.prepare_specs: list[dict[str, Any]] = _as_list(spec.get("prepare"))
        self.request_spec: dict[str, Any] = spec.get("request", {})
        self.rules: list[dict[str, Any]] = _as_list(spec.get("rules"))
        self.default_status = Status(spec.get("default", "unknown"))
        self.extract_spec: dict[str, str] = spec.get("extract", {}) or {}

    # ---------- 主流程 ----------
    async def check(self, ctx: CheckContext) -> Result:
        try:
            extra = self._resolve_env(self.info.requires)
        except LookupError as exc:
            return self.make_result(Status.SKIPPED, detail=str(exc))

        template_ctx = build_context(ctx.email, extra)

        with Timer() as timer:
            try:
                await self._run_prepare(ctx.client, template_ctx, ctx.timeout)
                request = self._build_request(ctx=template_ctx)
                response = await self._send(ctx.client, request, ctx.timeout)
            except TemplateError as exc:
                return self.make_result(
                    Status.ERROR,
                    elapsed_ms=timer.ms,
                    detail=f"规则引用了未知变量: {{{exc.args[0]}}}",
                )
            except PrepareError as exc:
                return self.make_result(
                    Status.ERROR, elapsed_ms=timer.ms, detail=str(exc)
                )
            except httpx.TimeoutException:
                return self.make_result(
                    Status.ERROR, elapsed_ms=timer.ms, detail="请求超时"
                )
            except httpx.HTTPError as exc:
                return self.make_result(
                    Status.ERROR, elapsed_ms=timer.ms, detail=f"网络错误: {exc}"
                )

        return self._evaluate(response, timer.elapsed_ms)

    # ---------- 预备请求（拿 CSRF token / cookie 等） ----------
    async def _run_prepare(
        self, client: httpx.AsyncClient, ctx: dict[str, Any], timeout: float
    ) -> None:
        for index, step in enumerate(self.prepare_specs):
            request = self._build_request(step, ctx)
            try:
                response = await self._send(client, request, timeout)
            except httpx.HTTPError as exc:
                raise PrepareError(f"预备请求 #{index + 1} 失败: {exc}") from exc
            self._save_values(step.get("save", {}), response, client, ctx)

    def _save_values(
        self,
        save_spec: dict[str, Any],
        response: httpx.Response,
        client: httpx.AsyncClient,
        ctx: dict[str, Any],
    ) -> None:
        for var, rule in (save_spec or {}).items():
            source = str(rule.get("from", "body_regex"))
            value: Any = None
            if source == "cookie":
                name = str(rule.get("name"))
                value = response.cookies.get(name) or client.cookies.get(name)
            elif source == "header":
                value = response.headers.get(str(rule.get("name")))
            elif source == "json":
                try:
                    value = json_path(response.json(), str(rule.get("path")))
                except (json.JSONDecodeError, ValueError):
                    value = None
            elif source == "body_regex":
                match = re.search(str(rule.get("pattern")), response.text, re.DOTALL)
                if match:
                    value = match.group(int(rule.get("group", 1)))
            else:
                raise RuleConfigError(f"未知的 save.from 类型: {source}")

            if value is None:
                if rule.get("required", True):
                    raise PrepareError(f"预备请求未能取到变量 {{{var}}}")
                value = rule.get("default", "")
            ctx[var] = value

    # ---------- 环境变量 ----------
    def _resolve_env(self, requires: list[str]) -> dict[str, Any]:
        env: dict[str, Any] = {}
        for key in requires:
            value = lookup_secret(key)
            if not value:
                raise LookupError(f"缺少所需的配置项 {key}（请在 .env 中设置）")
            env[f"env.{key}"] = value
        return env

    # ---------- 请求构造 ----------
    def _build_request(
        self, spec: dict[str, Any] | None = None, ctx: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        spec = self.request_spec if spec is None else spec
        assert ctx is not None
        method = str(spec.get("method", "GET")).upper()
        url = render(str(spec["url"]), ctx)
        headers = render_any(spec.get("headers", {}), ctx)
        params = render_any(spec.get("params", {}), ctx)

        request: dict[str, Any] = {
            "method": method,
            "url": url,
            "headers": headers,
            "params": params,
            "follow_redirects": bool(spec.get("follow_redirects", True)),
        }
        if "json" in spec:
            request["json"] = render_any(spec["json"], ctx)
        elif "data" in spec:
            request["data"] = render_any(spec["data"], ctx)
        return request

    async def _send(
        self, client: httpx.AsyncClient, request: dict[str, Any], timeout: float
    ) -> httpx.Response:
        return await client.request(
            request["method"],
            request["url"],
            headers=request.get("headers") or None,
            params=request.get("params") or None,
            json=request.get("json"),
            data=request.get("data"),
            timeout=timeout,
            follow_redirects=request["follow_redirects"],
        )

    # ---------- 判定 ----------
    def _evaluate(self, response: httpx.Response, elapsed_ms: int) -> Result:
        text = response.text
        try:
            body_json: Any = response.json()
        except (json.JSONDecodeError, ValueError):
            body_json = None

        scope = {
            "status": response.status_code,
            "text": text,
            "json": body_json,
            "headers": response.headers,
            "url": str(response.url),
        }

        for rule in self.rules:
            for condition, status in _CONDITION_TO_STATUS.items():
                if condition in rule and self._match(rule[condition], scope):
                    detail = rule.get("detail")
                    return self.make_result(
                        status,
                        elapsed_ms=elapsed_ms,
                        http_status=response.status_code,
                        detail=detail,
                        data=self._extract(scope),
                    )

        return self.make_result(
            self.default_status,
            elapsed_ms=elapsed_ms,
            http_status=response.status_code,
            detail=self.spec.get("default_detail"),
            data=self._extract(scope),
        )

    def _match(self, condition: dict[str, Any], scope: dict[str, Any]) -> bool:
        """一条条件里的所有子句需全部成立（AND）。"""
        for key, expected in condition.items():
            if not self._match_clause(key, expected, scope):
                return False
        return True

    def _match_clause(self, key: str, expected: Any, scope: dict[str, Any]) -> bool:
        if key == "status_in":
            return scope["status"] in _as_list(expected)
        if key == "status_eq":
            return scope["status"] == expected
        if key == "body_contains":
            return all(str(s) in scope["text"] for s in _as_list(expected))
        if key == "body_not_contains":
            return all(str(s) not in scope["text"] for s in _as_list(expected))
        if key == "body_matches":
            return bool(re.search(str(expected), scope["text"], re.IGNORECASE | re.DOTALL))
        if key == "json_path_exists":
            return json_path(scope["json"], str(expected)) is not None
        if key == "json_path_equals":
            actual = json_path(scope["json"], str(expected.get("path")))
            return actual == expected.get("value")
        if key == "json_path_truthy":
            return bool(json_path(scope["json"], str(expected)))
        if key == "header_contains":
            header = scope["headers"].get(str(expected.get("name")), "")
            return str(expected.get("value", "")).lower() in header.lower()
        raise RuleConfigError(f"未知的规则子句: {key}")

    def _extract(self, scope: dict[str, Any]) -> dict[str, Any]:
        data: dict[str, Any] = {}
        for field, path in self.extract_spec.items():
            value = json_path(scope["json"], str(path))
            if value is not None:
                data[field] = value
        return data


def build_provider_info(spec: dict[str, Any], source: str) -> ProviderInfo:
    requires = _as_list(spec.get("requires"))
    missing = [key for key in requires if not lookup_secret(key)]
    return ProviderInfo(
        name=spec.get("name", source),
        title=spec.get("title", spec.get("name", source)),
        category=spec.get("category", "other"),
        homepage=spec.get("homepage"),
        description=spec.get("description"),
        notes=spec.get("notes"),
        requires=requires,
        kind="declarative",
        enabled=bool(spec.get("enabled", True)),
        ready=not missing,
        unready_reason=(
            f"需要配置: {', '.join(missing)}" if missing else None
        ),
    )
