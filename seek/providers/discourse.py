"""Side-effect-free Discourse account checks with a live privacy guard."""

from __future__ import annotations

import asyncio
from collections import deque
import logging
from pathlib import Path
import re
import time
from typing import Any
from urllib.parse import urlsplit

import httpx
import yaml

from ..models import ProviderInfo, Result, Status
from .base import CheckContext, Provider, Timer

log = logging.getLogger(__name__)

_TAKEN_RE = re.compile(
    r"(already.{0,30}taken|has already been taken|已被使用|已被占用|已经被使用)",
    re.IGNORECASE | re.DOTALL,
)


def _find_key(value: object, wanted: str) -> object | None:
    if isinstance(value, dict):
        if wanted in value:
            return value[wanted]
        for child in value.values():
            found = _find_key(child, wanted)
            if found is not None:
                return found
    elif isinstance(value, list):
        for child in value:
            found = _find_key(child, wanted)
            if found is not None:
                return found
    return None


class DiscourseProvider(Provider):
    """Check Discourse's read-only signup validation endpoint.

    Modern Discourse can deliberately return ``success: OK`` for every email
    when ``hide_email_address_taken`` is enabled.  The public client setting is
    therefore checked first; an unavailable or hidden setting always produces
    UNKNOWN rather than a false NOT_REGISTERED verdict.
    """

    # Upstream silently returns success_json after 10 checks/minute. Keep a
    # local safety margin so that silent throttling cannot become a false
    # negative. Each provider instance has its own window.
    _MAX_CHECKS_PER_MINUTE = 8

    def __init__(self, *, name: str, title: str, homepage: str, audited_at: str) -> None:
        parts = urlsplit(homepage.rstrip("/"))
        self._base_url = f"{parts.scheme}://{parts.netloc}"
        self._recent_checks: deque[float] = deque()
        self._rate_lock = asyncio.Lock()
        super().__init__(
            ProviderInfo(
                name=name,
                title=title,
                category="forum",
                homepage=homepage.rstrip("/"),
                description="Discourse 公开只读邮箱可用性校验（带实时隐私设置保护）",
                notes=(
                    "不发送验证码、激活邮件或找回邮件；"
                    f"最近双域名负样本审计：{audited_at}"
                ),
                kind="builtin",
            )
        )

    async def _reserve_check(self) -> bool:
        now = time.monotonic()
        async with self._rate_lock:
            while self._recent_checks and now - self._recent_checks[0] >= 60.0:
                self._recent_checks.popleft()
            if len(self._recent_checks) >= self._MAX_CHECKS_PER_MINUTE:
                return False
            self._recent_checks.append(now)
            return True

    async def check(self, ctx: CheckContext) -> Result:
        with Timer() as timer:
            try:
                settings_response = await ctx.client.get(
                    f"{self._base_url}/site/settings.json",
                    headers={"Accept": "application/json"},
                    timeout=ctx.timeout,
                    follow_redirects=True,
                )
            except httpx.TimeoutException:
                return self.make_result(
                    Status.ERROR, elapsed_ms=timer.ms, detail="读取论坛隐私设置超时"
                )
            except httpx.HTTPError as exc:
                return self.make_result(
                    Status.ERROR,
                    elapsed_ms=timer.ms,
                    detail=f"读取论坛隐私设置失败: {type(exc).__name__}",
                )

            if settings_response.status_code in (403, 429):
                return self.make_result(
                    Status.RATE_LIMITED,
                    elapsed_ms=timer.ms,
                    http_status=settings_response.status_code,
                    detail="论坛阻止了隐私设置校验",
                )

            try:
                setting = _find_key(
                    settings_response.json(), "hide_email_address_taken"
                )
            except ValueError:
                setting = None

            if setting is True:
                return self.make_result(
                    Status.UNKNOWN,
                    elapsed_ms=timer.ms,
                    http_status=settings_response.status_code,
                    detail="论坛已隐藏邮箱占用状态，无法可靠判断",
                )
            if setting is not False:
                return self.make_result(
                    Status.UNKNOWN,
                    elapsed_ms=timer.ms,
                    http_status=settings_response.status_code,
                    detail="无法确认论坛是否公开邮箱占用状态",
                )

            if not await self._reserve_check():
                return self.make_result(
                    Status.RATE_LIMITED,
                    elapsed_ms=timer.ms,
                    detail="已达到论坛安全校验频率上限，请稍后重试",
                )

            try:
                response = await ctx.client.get(
                    f"{self._base_url}/u/check_email.json",
                    params={"email": ctx.email},
                    headers={
                        "Accept": "application/json",
                        "Referer": f"{self._base_url}/signup",
                    },
                    timeout=ctx.timeout,
                    follow_redirects=True,
                )
            except httpx.TimeoutException:
                return self.make_result(
                    Status.ERROR, elapsed_ms=timer.ms, detail="论坛邮箱校验超时"
                )
            except httpx.HTTPError as exc:
                return self.make_result(
                    Status.ERROR,
                    elapsed_ms=timer.ms,
                    detail=f"论坛邮箱校验失败: {type(exc).__name__}",
                )

        if response.status_code in (403, 429):
            return self.make_result(
                Status.RATE_LIMITED,
                elapsed_ms=timer.elapsed_ms,
                http_status=response.status_code,
                detail="论坛拒绝或限制了邮箱校验",
            )

        try:
            payload: Any = response.json()
        except ValueError:
            payload = None

        if response.status_code == 200 and isinstance(payload, dict):
            if payload.get("success") == "OK":
                return self.make_result(
                    Status.NOT_REGISTERED,
                    elapsed_ms=timer.elapsed_ms,
                    http_status=response.status_code,
                    detail="论坛注册校验确认该邮箱当前可用",
                )
            if _TAKEN_RE.search(str(payload)):
                return self.make_result(
                    Status.REGISTERED,
                    elapsed_ms=timer.elapsed_ms,
                    http_status=response.status_code,
                    detail="论坛注册校验确认该邮箱已被占用",
                )

        return self.make_result(
            Status.UNKNOWN,
            elapsed_ms=timer.elapsed_ms,
            http_status=response.status_code,
            detail="论坛未返回明确的邮箱占用状态",
        )


def load_discourse_providers(path: Path) -> list[Provider]:
    if not path.exists():
        log.warning("Discourse site list does not exist: %s", path)
        return []
    try:
        specs = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        log.error("Failed to load Discourse site list %s: %s", path, exc)
        return []
    if not isinstance(specs, list):
        log.error("Discourse site list must be a YAML list: %s", path)
        return []

    providers: list[Provider] = []
    seen: set[str] = set()
    for index, spec in enumerate(specs, 1):
        try:
            name = str(spec["name"]).strip().lower()
            title = str(spec["title"]).strip()
            homepage = str(spec["homepage"]).strip().rstrip("/")
            audited_at = str(spec["audited_at"]).strip()
            parts = urlsplit(homepage)
            if parts.scheme != "https" or not parts.netloc:
                raise ValueError("homepage must be an absolute HTTPS URL")
            if not name or name in seen:
                raise ValueError("name is empty or duplicated")
            seen.add(name)
            providers.append(
                DiscourseProvider(
                    name=name,
                    title=title,
                    homepage=homepage,
                    audited_at=audited_at,
                )
            )
        except (KeyError, TypeError, ValueError) as exc:
            log.error("Invalid Discourse site entry #%d: %s", index, exc)
    return providers
