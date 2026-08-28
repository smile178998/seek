"""Audit uncurated user-scanner email modules with harmless negative controls.

This helper intentionally excludes every module known to send password-reset,
login-code, username-reminder, or signup-OTP messages.  It is a maintainer tool;
normal scans never call it.
"""

from __future__ import annotations

import argparse
import asyncio
from datetime import UTC, datetime
import importlib
import json
import secrets
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from seek.providers.user_scanner_bridge import (
    SIDE_EFFECTFUL_MODULES,
    VALIDATOR_ALIASES,
)


def _entries(root: Path) -> list[str]:
    entries: list[str] = []
    for path in root.glob("*/*.py"):
        if path.name == "__init__.py":
            continue
        entries.append(f"{path.parent.name}/{path.stem}")
    return sorted(entries)


def _curated(path: Path) -> set[str]:
    return {
        line.strip()
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    }


async def _check(entry: str, email: str) -> dict[str, str | None]:
    category, module_name = entry.split("/", 1)
    module = importlib.import_module(
        f"user_scanner.email_scan.{category}.{module_name}"
    )
    validator_name = VALIDATOR_ALIASES.get(entry, f"validate_{module_name}")
    validator = getattr(module, validator_name)
    try:
        outcome = await asyncio.wait_for(validator(email), timeout=55.0)
    except Exception as exc:
        return {
            "email_domain": email.rsplit("@", 1)[-1],
            "status": "ERROR",
            "reason": f"{type(exc).__name__}: {exc}",
        }
    return {
        "email_domain": email.rsplit("@", 1)[-1],
        "status": outcome.status.name,
        "reason": outcome.get_reason() or None,
    }


async def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    parser.add_argument("--concurrency", type=int, default=4)
    args = parser.parse_args()

    import user_scanner

    package_root = Path(user_scanner.__file__).resolve().parent
    email_scan_root = package_root / "email_scan"
    curated_path = Path(__file__).resolve().parents[1] / "seek" / "data" / "user_scanner_reliable.txt"
    curated = _curated(curated_path)
    candidates = [
        entry
        for entry in _entries(email_scan_root)
        if entry not in curated and entry not in SIDE_EFFECTFUL_MODULES
    ]

    controls = [
        f"seek-audit-{secrets.token_hex(10)}@gmail.com",
        f"seek-audit-{secrets.token_hex(10)}@outlook.com",
    ]
    semaphore = asyncio.Semaphore(max(1, args.concurrency))

    async def audit(entry: str) -> dict[str, object]:
        async with semaphore:
            observations = [await _check(entry, email) for email in controls]
            row: dict[str, object] = {
                "module": entry,
                "passed": all(row["status"] == "AVAILABLE" for row in observations),
                "observations": observations,
            }
            print(json.dumps(row, ensure_ascii=False), flush=True)
            return row

    rows = await asyncio.gather(*(audit(entry) for entry in candidates))

    report = {
        "audited_at": datetime.now(UTC).isoformat(),
        "method": "two random negative controls (gmail.com + outlook.com)",
        "side_effectful_modules_excluded": sorted(SIDE_EFFECTFUL_MODULES),
        "candidates": rows,
    }
    if args.output:
        args.output.write_text(
            json.dumps(report, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )


if __name__ == "__main__":
    asyncio.run(main())
