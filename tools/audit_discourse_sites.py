"""Live-audit candidate Discourse email-availability endpoints.

Only the read-only ``GET /u/check_email.json`` endpoint is called.  The two
high-entropy controls are not accounts and no signup, reset, activation, or
message-sending endpoint is used.
"""

from __future__ import annotations

import argparse
import asyncio
from datetime import UTC, datetime
import html
import json
import re
import secrets
from pathlib import Path
from urllib.parse import urlsplit

import httpx
import yaml


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


async def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--candidates",
        type=Path,
        default=Path(__file__).with_name("discourse_candidates.yaml"),
    )
    parser.add_argument("--output", type=Path)
    parser.add_argument("--concurrency", type=int, default=8)
    parser.add_argument("--only")
    args = parser.parse_args()

    candidates = yaml.safe_load(args.candidates.read_text(encoding="utf-8"))
    if args.only:
        wanted = {name.strip() for name in args.only.split(",") if name.strip()}
        candidates = [site for site in candidates if site["name"] in wanted]
    controls = [
        f"seek-audit-{secrets.token_hex(10)}@gmail.com",
        f"seek-audit-{secrets.token_hex(10)}@outlook.com",
    ]
    semaphore = asyncio.Semaphore(max(1, args.concurrency))

    async with httpx.AsyncClient(
        timeout=18.0,
        follow_redirects=True,
        headers={
            "Accept": "application/json",
            "User-Agent": "seek-provider-audit/1.0 (+authorized maintenance)",
        },
    ) as client:

        async def check(site: dict[str, str], email: str) -> dict[str, object]:
            homepage = site["homepage"].rstrip("/")
            parts = urlsplit(homepage)
            base = f"{parts.scheme}://{parts.netloc}"
            # A few communities live below a path. Discourse's user route is
            # still rooted at the host, so deliberately query the origin.
            endpoint = f"{base}/u/check_email.json"
            try:
                response = await client.get(
                    endpoint,
                    params={"email": email},
                    headers={"Referer": f"{base}/signup"},
                )
                try:
                    payload = response.json()
                except ValueError:
                    payload = None
                success = payload.get("success") if isinstance(payload, dict) else None
                return {
                    "email_domain": email.rsplit("@", 1)[-1],
                    "status": response.status_code,
                    "final_host": response.url.host,
                    "success": success,
                    "body": response.text[:180].replace("\r", " ").replace("\n", " "),
                }
            except Exception as exc:
                return {
                    "email_domain": email.rsplit("@", 1)[-1],
                    "error": f"{type(exc).__name__}: {exc}",
                }

        async def audit(site: dict[str, str]) -> dict[str, object]:
            async with semaphore:
                observations = [await check(site, email) for email in controls]
                parts = urlsplit(site["homepage"])
                base = f"{parts.scheme}://{parts.netloc}"
                try:
                    settings_response = await client.get(f"{base}/site/settings.json")
                    settings_payload = settings_response.json()
                    setting_value = _find_key(
                        settings_payload, "hide_email_address_taken"
                    )
                    if isinstance(setting_value, bool):
                        hide_email_address_taken = setting_value
                    elif isinstance(setting_value, str) and setting_value.lower() in {
                        "true",
                        "false",
                    }:
                        hide_email_address_taken = setting_value.lower() == "true"
                    else:
                        hide_email_address_taken = None
                except Exception:
                    # Older Discourse versions embed client settings in the
                    # initial HTML instead of exposing /site/settings.json.
                    try:
                        homepage = await client.get(base)
                        source = html.unescape(homepage.text).replace("\\\"", '"')
                        setting_match = re.search(
                            r'"hide_email_address_taken"\s*:\s*(true|false)',
                            source,
                            re.IGNORECASE,
                        )
                        hide_email_address_taken = (
                            setting_match.group(1).lower() == "true"
                            if setting_match
                            else None
                        )
                    except Exception:
                        hide_email_address_taken = None
            endpoint_healthy = all(
                row.get("status") == 200 and row.get("success") == "OK"
                for row in observations
            )
            # Discourse can intentionally make every address look available.
            # Such a site is reachable but cannot provide an account signal.
            passed = endpoint_healthy and hide_email_address_taken is False
            row: dict[str, object] = {
                **site,
                "passed": passed,
                "endpoint_healthy": endpoint_healthy,
                "hide_email_address_taken": hide_email_address_taken,
                "observations": observations,
            }
            print(json.dumps(row, ensure_ascii=False), flush=True)
            return row

        rows = await asyncio.gather(*(audit(site) for site in candidates))

    report = {
        "audited_at": datetime.now(UTC).isoformat(),
        "method": (
            "read-only Discourse check_email endpoint with two random negative controls; "
            "requires public hide_email_address_taken=false"
        ),
        "passed": [row for row in rows if row["passed"]],
        "failed": [row for row in rows if not row["passed"]],
    }
    if args.output:
        args.output.write_text(
            json.dumps(report, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )


if __name__ == "__main__":
    asyncio.run(main())
