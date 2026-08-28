"""Bridge for the actively maintained ``user-scanner`` email modules."""

from __future__ import annotations

import asyncio
import concurrent.futures
import html
import importlib
import logging
from pathlib import Path
from types import ModuleType
from typing import Any

from ..models import ProviderInfo, Result, Status
from .base import CheckContext, Provider, Timer

log = logging.getLogger(__name__)

# 部分上游模块虽声明为 async，内部仍会执行阻塞式 DNS/TLS 代码。若直接放在
# FastAPI 的事件循环里，它们会让进度推送和 asyncio 超时一起失效。每个模块改在
# 独立线程与独立事件循环运行，主扫描器便能严格执行自己的截止时间。
_SCANNER_EXECUTOR = concurrent.futures.ThreadPoolExecutor(
    max_workers=24, thread_name_prefix="seek-user-scanner"
)

# Upstream modules use a 15 second timeout per HTTP request, and some checks
# perform as many as three sequential requests (page, token, account lookup).
# The wrapper therefore needs a whole-check budget, not a per-request budget.
# Fast modules still stream their result immediately; only genuinely slow
# multi-step checks consume the larger allowance.
USER_SCANNER_TIMEOUT = 50.0

CATEGORY_MAP = {
    "adult": "adult",
    "community": "forum",
    "creator": "profile",
    "crm": "crm",
    "dating": "dating",
    "dev": "dev",
    "entertainment": "media",
    "fitness": "sport",
    "gaming": "media",
    "hosting": "dev",
    "jobs": "jobs",
    "learning": "edu",
    "music": "music",
    "news": "media",
    "other": "other",
    "shopping": "shop",
    "social": "social",
    "sports": "sport",
    "travel": "transport",
    "women_health": "medical",
}

# A small number of upstream modules expose a validator whose function name
# does not match the module name expected by user-scanner's generic engine.
# Keep the compatibility mapping here rather than modifying site-packages.
VALIDATOR_ALIASES = {
    "sports/besoccer": "validate_okcats",
}

# These upstream modules trigger password-reset, login-code, username-reminder,
# or signup-OTP delivery.  They must never be loaded by seek's quiet scanner,
# even if somebody accidentally adds them to the curated module file later.
# The list was reviewed against user-scanner 1.5.0.2 on 2026-08-28.
SIDE_EFFECTFUL_MODULES = frozenset(
    {
        "adult/babestation",
        "adult/fantasia",
        "adult/flirtbate",
        "adult/made_porn",
        "adult/sexvid",
        "creator/buymeacoffee",
        "creator/gumroad",
        "dev/luarocks",
        "entertainment/anilist",
        "entertainment/hoichoi",
        "entertainment/weverse",
        "fitness/finch",
        "learning/asafeer",
        "learning/bnrlanguages",
        "learning/bunpo",
        "learning/cambly",
        "learning/hellochinese",
        "learning/hanzii",
        "learning/heyjapan",
        "learning/programminghub",
        "learning/talkpal",
        "other/ama",
        "other/dragongroot",
        "social/couplejoy",
        "social/slowly",
        "social/superlive",
        "sports/uniscore",
    }
)


def user_scanner_available() -> bool:
    try:
        import user_scanner.core.engine  # noqa: F401
    except Exception:
        return False
    return True


def _map_status(status_name: str, reason: str) -> Status:
    text = html.unescape(reason or "").lower()
    unsupported_markers = (
        "don't accept this email service",
        "does not accept this email service",
        "does not accept registrations from",
        "does not support the sub-address probe",
        "email service is not accepted",
        "email delivery issues",
    )
    if any(marker in text for marker in unsupported_markers):
        return Status.UNKNOWN
    if status_name == "TAKEN":
        return Status.REGISTERED
    if status_name == "AVAILABLE":
        return Status.NOT_REGISTERED
    if status_name == "SKIPPED":
        return Status.SKIPPED
    if any(marker in text for marker in ("429", "403", "rate limit", "waf", "blocked")):
        return Status.RATE_LIMITED
    return Status.ERROR


def _normalize_profile_data(
    extra: dict[str, Any] | None, media: dict[str, Any] | None
) -> dict[str, Any]:
    """Normalize public profile fields returned by upstream modules."""
    data: dict[str, Any] = dict(extra or {})
    aliases = {
        "name": "display_name",
        "id": "user_id",
        "profile": "profile_url",
        "profileUrl": "profile_url",
    }
    for source, target in aliases.items():
        if source in data and target not in data:
            data[target] = data.pop(source)

    media_data = dict(media or {})
    avatar = media_data.pop("avatar", None) or media_data.pop("profile_picture", None)
    if isinstance(avatar, str) and avatar.strip() and avatar.strip().lower() != "no pfp":
        avatar = avatar.strip()
        if avatar.startswith("//"):
            avatar = "https:" + avatar
        data["avatar_url"] = avatar
    if media_data:
        data["media"] = media_data
    return data


class UserScannerProvider(Provider):
    def __init__(self, module: ModuleType, category: str, module_name: str) -> None:
        from user_scanner.core.helpers import get_site_name

        self._module = module
        self._entry = f"{category}/{module_name}"
        self.module_name = module_name
        super().__init__(
            ProviderInfo(
                name=f"userscanner_{module_name}",
                title=get_site_name(module),
                category=CATEGORY_MAP.get(category, "other"),
                description=f"User Scanner live-tested module · {module_name}",
                notes="Maintained by user-scanner; only modules passing two live negative-control runs are enabled",
                kind="builtin",
            )
        )

    def execution_timeout(self, ctx: CheckContext) -> float:
        return max(ctx.timeout + 2.0, USER_SCANNER_TIMEOUT + 2.0)

    async def check(self, ctx: CheckContext) -> Result:
        from user_scanner.core import engine as scanner_engine

        def run_isolated():
            validator_name = VALIDATOR_ALIASES.get(self._entry)
            if validator_name:
                validator = getattr(self._module, validator_name)
                return asyncio.run(validator(ctx.email))
            return asyncio.run(scanner_engine.check(self._module, ctx.email))

        with Timer() as timer:
            try:
                loop = asyncio.get_running_loop()
                outcome = await asyncio.wait_for(
                    loop.run_in_executor(_SCANNER_EXECUTOR, run_isolated),
                    timeout=max(ctx.timeout, USER_SCANNER_TIMEOUT),
                )
            except asyncio.TimeoutError:
                return self.make_result(
                    Status.ERROR,
                    elapsed_ms=timer.ms,
                    detail="User Scanner module timed out",
                )
            except Exception as exc:
                return self.make_result(
                    Status.ERROR,
                    elapsed_ms=timer.ms,
                    detail=f"User Scanner error: {type(exc).__name__}: {exc}",
                )

        reason = html.unescape(outcome.get_reason() or "")
        status = _map_status(outcome.status.name, reason)
        data = _normalize_profile_data(outcome.extra, outcome.media)
        result = self.make_result(
            status,
            elapsed_ms=timer.elapsed_ms,
            detail=reason or None,
            data=data,
        )
        if outcome.url:
            result.homepage = outcome.url
        return result


def discover_user_scanner_entries() -> list[str]:
    """Return every email module shipped by the installed upstream package."""
    try:
        import user_scanner
    except Exception:
        return []

    root = Path(user_scanner.__file__).resolve().parent / "email_scan"
    return sorted(
        f"{path.parent.name}/{path.stem}"
        for path in root.glob("*/*.py")
        if path.name != "__init__.py"
    )


def _curated_entries(module_file: Path) -> list[str]:
    if not module_file.exists():
        log.warning("user-scanner module list does not exist: %s", module_file)
        return []
    return [
        line.strip()
        for line in module_file.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    ]


def load_user_scanner_providers(
    module_file: Path, *, include_all: bool = False
) -> list[Provider]:
    if not user_scanner_available():
        log.info("user-scanner is not installed; skipping its modules")
        return []

    curated = set(_curated_entries(module_file))
    entries = set(curated)
    if include_all:
        entries.update(discover_user_scanner_entries())

    providers: list[Provider] = []
    for entry in sorted(entries):
        if entry in SIDE_EFFECTFUL_MODULES:
            message = "skipping side-effectful user-scanner module: %s"
            if entry in curated:
                log.warning(message, entry)
            else:
                log.debug(message, entry)
            continue
        try:
            category, module_name = entry.split("/", 1)
            module = importlib.import_module(
                f"user_scanner.email_scan.{category}.{module_name}"
            )
            provider = UserScannerProvider(module, category, module_name)
            if entry not in curated:
                provider.info.description = (
                    f"User Scanner extended-profile candidate · {module_name}"
                )
                provider.info.notes = (
                    "Maintained by user-scanner; excluded from the reliable profile "
                    "because the latest live audit was inconclusive"
                )
            providers.append(provider)
        except Exception as exc:
            log.warning("failed to load user-scanner module %s: %s", entry, exc)
    return providers
