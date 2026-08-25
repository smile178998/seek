"""Repeatable live checks for the curated reliable provider set.

The audit uses two high-entropy negative controls on established mail domains.
Only providers that explicitly report both controls as not registered pass.  It
never loads known password-reset or OTP-sending user-scanner modules; that
invariant is enforced by :mod:`seek.providers.user_scanner_bridge`.
"""

from __future__ import annotations

import secrets
from datetime import UTC, datetime
from typing import Any

from .config import Settings, get_settings
from .engine import Engine
from .models import Status
from .providers.registry import load_providers


NON_ACCOUNT_PROVIDERS = frozenset({"mx", "mail_provider", "disposable"})


async def audit_reliable_providers(
    settings: Settings | None = None,
) -> dict[str, Any]:
    """Run two negative controls through every account provider in reliable mode."""

    settings = settings or get_settings()
    token = secrets.token_hex(10)
    controls = (
        f"seek.audit.{token}@gmail.com",
        f"seek.audit.{token}@outlook.com",
    )
    providers = [
        provider
        for provider in load_providers(
            settings, profile="reliable", include_holehe=True
        )
        if provider.info.name not in NON_ACCOUNT_PROVIDERS
    ]
    observations: dict[str, list[dict[str, Any]]] = {
        provider.info.name: [] for provider in providers
    }

    for control in controls:
        async with Engine(providers, settings=settings) as engine:
            response = await engine.scan(control)
        for result in response.results:
            observations[result.provider].append(
                {
                    "status": result.status.value,
                    "detail": result.detail,
                    "http_status": result.http_status,
                    "elapsed_ms": result.elapsed_ms,
                }
            )

    passed: list[str] = []
    failed: list[dict[str, Any]] = []
    for provider in providers:
        rows = observations[provider.info.name]
        if len(rows) == len(controls) and all(
            row["status"] == Status.NOT_REGISTERED.value for row in rows
        ):
            passed.append(provider.info.name)
        else:
            failed.append({"provider": provider.info.name, "observations": rows})

    return {
        "audited_at": datetime.now(UTC).isoformat(),
        "method": "two random negative controls (gmail.com + outlook.com)",
        "control_domains": ["gmail.com", "outlook.com"],
        "total": len(providers),
        "passed": passed,
        "failed": failed,
    }
