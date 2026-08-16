"""多工具聚合层：把同类「邮箱注册痕迹」工具跑一遍，汇总证据给 AI 总结。

档位：
  reliable — 白名单规则 + 经筛选的 Holehe 模块 + Gravatar + 网页搜索 (+ socialscan)
  full     — 全部 seek 规则 + Holehe（应用禁用清单）+ 其余工具

说明：没有任何工具能保证「找出所有注册网站」；可靠模式优先给出明确判定。
"""

from __future__ import annotations

import asyncio
import hashlib
import json
import logging
import re
from typing import Any, Awaitable, Callable
from urllib.parse import quote_plus

import httpx

from .config import Settings, build_ssl_verify
from .engine import Engine
from .models import Result, Status
from .providers.holehe_bridge import holehe_available, load_holehe_providers
from .providers.registry import load_providers

log = logging.getLogger(__name__)

Emit = Callable[[str, dict[str, Any]], Awaitable[None] | None]


async def _emit(emit: Emit | None, event: str, data: dict[str, Any]) -> None:
    if not emit:
        return
    result = emit(event, data)
    if hasattr(result, "__await__"):
        await result  # type: ignore[misc]


def _digest_sha256(email: str) -> str:
    return hashlib.sha256(email.strip().lower().encode("utf-8")).hexdigest()


def _compact_results(results: list[Result], source: str) -> dict[str, Any]:
    confirmed = []
    info = []
    not_reg: list[dict[str, Any]] = []
    noise = []
    for r in results:
        item = {
            "source": source,
            "provider": r.provider,
            "title": r.title,
            "status": r.status.value,
            "detail": r.detail,
            "homepage": r.homepage,
            "data": r.data or {},
        }
        if r.status is Status.REGISTERED:
            confirmed.append(item)
        elif r.status is Status.INFO:
            info.append(item)
        elif r.status is Status.NOT_REGISTERED:
            not_reg.append({
                "source": source,
                "title": r.title,
                "status": r.status.value,
                "detail": r.detail,
                "homepage": r.homepage,
            })
        else:
            noise.append({"title": r.title, "status": r.status.value, "detail": r.detail})
    return {
        "source": source,
        "total": len(results),
        "registered": confirmed,
        "info": info,
        "not_registered": not_reg[:40],
        "not_registered_count": len(not_reg),
        "failed_or_unknown": noise[:50],
        "failed_or_unknown_count": len(noise),
        "effective_count": len(confirmed) + len(info) + len(not_reg),
    }


async def run_seek_rules(
    email: str,
    settings: Settings,
    emit: Emit | None = None,
    profile: str = "reliable",
) -> dict[str, Any]:
    resolved_profile = settings.normalize_profile(profile, kind="scan")
    # full 档的 Holehe 由 run_holehe() 单独跑，避免重复；reliable 档只保留白名单模块。
    providers = load_providers(
        settings,
        profile=resolved_profile,
        include_holehe=resolved_profile == "reliable",
    )
    await _emit(emit, "backend_start", {
        "name": "seek_rules",
        "modules": len(providers),
        "profile": resolved_profile,
    })
    async with Engine(providers, settings) as engine:
        response = await engine.scan(email)
    for r in response.results:
        # 可靠模式下把明确判定都推到前端，避免界面像「没结果」
        if r.status in (Status.REGISTERED, Status.INFO, Status.NOT_REGISTERED):
            await _emit(emit, "result", r.model_dump(mode="json"))
    out = _compact_results(response.results, "seek_rules")
    await _emit(emit, "backend_done", {
        "name": "seek_rules",
        "total": out["total"],
        "registered_count": len(out["registered"]),
        "not_registered_count": out["not_registered_count"],
        "info_count": len(out["info"]),
        "failed_or_unknown_count": out["failed_or_unknown_count"],
        "effective_count": out["effective_count"],
    })
    return out


async def run_holehe(
    email: str,
    settings: Settings,
    emit: Emit | None = None,
) -> dict[str, Any]:
    if not holehe_available():
        await _emit(emit, "backend_skip", {"name": "holehe", "reason": "未安装 holehe（pip install holehe）"})
        return {"source": "holehe", "available": False, "error": "holehe 未安装", "registered": [], "info": []}

    disabled = settings.disabled_holehe()
    providers = []
    for provider in load_holehe_providers():
        short = provider.info.name
        if short.startswith("holehe_"):
            short = short[len("holehe_") :]
        if short in disabled:
            continue
        providers.append(provider)

    await _emit(emit, "backend_start", {
        "name": "holehe",
        "modules": len(providers),
        "disabled_skipped": len(disabled),
    })
    async with Engine(providers, settings) as engine:
        response = await engine.scan(email)
    for r in response.results:
        if r.status in (Status.REGISTERED, Status.INFO):
            payload = r.model_dump(mode="json")
            payload["title"] = f"[Holehe] {r.title}"
            await _emit(emit, "result", payload)
    out = _compact_results(response.results, "holehe")
    out["available"] = True
    await _emit(emit, "backend_done", {
        "name": "holehe",
        "total": out["total"],
        "registered_count": len(out["registered"]),
        "not_registered_count": out["not_registered_count"],
        "failed_or_unknown_count": out["failed_or_unknown_count"],
        "effective_count": out["effective_count"],
    })
    return out


async def run_gravatar(
    email: str,
    settings: Settings,
    emit: Emit | None = None,
) -> dict[str, Any]:
    await _emit(emit, "backend_start", {"name": "gravatar", "modules": 1})
    sha = _digest_sha256(email)
    headers = {"User-Agent": settings.user_agent, "Accept": "application/json"}
    if getattr(settings, "_accept_language_override", None):
        headers["Accept-Language"] = getattr(settings, "_accept_language_override")
    result: dict[str, Any] = {
        "source": "gravatar",
        "registered": False,
        "profile": None,
        "avatar": False,
    }
    async with httpx.AsyncClient(
        timeout=settings.timeout,
        verify=build_ssl_verify(settings),
        proxy=settings.proxy or None,
        headers=headers,
    ) as client:
        try:
            avatar = await client.get(
                f"https://www.gravatar.com/avatar/{sha}",
                params={"d": "404"},
            )
            result["avatar"] = avatar.status_code == 200
        except httpx.HTTPError as exc:
            result["avatar_error"] = str(exc)
        try:
            profile = await client.get(f"https://www.gravatar.com/{sha}.json")
            if profile.status_code == 200:
                data = profile.json()
                entry = (data.get("entry") or [{}])[0]
                result["registered"] = True
                result["profile"] = {
                    "username": entry.get("preferredUsername"),
                    "display_name": entry.get("displayName"),
                    "profile_url": entry.get("profileUrl"),
                    "accounts": [
                        a.get("shortname") for a in (entry.get("accounts") or []) if a.get("shortname")
                    ],
                    "urls": [u.get("value") for u in (entry.get("urls") or []) if u.get("value")],
                }
                await _emit(emit, "result", {
                    "provider": "gravatar_ai",
                    "title": "Gravatar 公开资料",
                    "category": "profile",
                    "homepage": "https://gravatar.com",
                    "status": "registered",
                    "detail": "存在公开 Gravatar 资料",
                    "elapsed_ms": 0,
                    "http_status": 200,
                    "data": result["profile"],
                })
            else:
                await _emit(emit, "result", {
                    "provider": "gravatar_ai",
                    "title": "Gravatar 公开资料",
                    "category": "profile",
                    "homepage": "https://gravatar.com",
                    "status": "not_registered",
                    "detail": "无公开 Gravatar 资料",
                    "elapsed_ms": 0,
                    "http_status": profile.status_code,
                    "data": {},
                })
        except httpx.HTTPError as exc:
            result["profile_error"] = str(exc)

    await _emit(emit, "backend_done", {"name": "gravatar", "registered": result["registered"]})
    return result


async def run_web_searches(
    email: str,
    settings: Settings,
    emit: Emit | None = None,
) -> dict[str, Any]:
    await _emit(emit, "backend_start", {"name": "web_search", "modules": 3})
    queries = [
        f'"{email}"',
        f'"{email}" account OR profile OR registered',
        f'"{email}" site:github.com OR site:twitter.com OR site:linkedin.com',
    ]
    all_results: list[dict[str, Any]] = []
    web_headers = {"User-Agent": "Mozilla/5.0 (compatible; seek-osint/0.1)"}
    if getattr(settings, "_accept_language_override", None):
        web_headers["Accept-Language"] = getattr(settings, "_accept_language_override")
    async with httpx.AsyncClient(
        timeout=20.0,
        verify=build_ssl_verify(settings),
        proxy=settings.proxy or None,
        headers=web_headers,
        follow_redirects=True,
    ) as client:
        for q in queries:
            try:
                resp = await client.get(f"https://html.duckduckgo.com/html/?q={quote_plus(q)}")
                links = re.findall(
                    r'class="result__a"[^>]*href="([^"]+)"[^>]*>(.*?)</a>',
                    resp.text,
                    flags=re.I | re.S,
                )
                snippets = re.findall(
                    r'class="result__snippet"[^>]*>(.*?)</(?:a|td|div)',
                    resp.text,
                    flags=re.I | re.S,
                )
                for i, (href, title) in enumerate(links[:6]):
                    all_results.append({
                        "query": q,
                        "title": _strip_tags(title)[:120],
                        "url": href,
                        "snippet": _strip_tags(snippets[i])[:200] if i < len(snippets) else "",
                    })
            except httpx.HTTPError as exc:
                all_results.append({"query": q, "error": str(exc)})

    seen = set()
    unique = []
    for item in all_results:
        u = item.get("url")
        if not u or u in seen:
            continue
        seen.add(u)
        unique.append(item)

    await _emit(emit, "backend_done", {"name": "web_search", "hits": len(unique)})
    return {"source": "web_search", "results": unique[:20]}


async def run_socialscan(
    email: str,
    settings: Settings,
    emit: Emit | None = None,
) -> dict[str, Any]:
    """可选：调用 socialscan 库（若已安装）。"""
    try:
        from socialscan.util import Platforms, sync_execute_queries  # type: ignore
    except Exception:
        await _emit(emit, "backend_skip", {"name": "socialscan", "reason": "未安装（可选 pip install socialscan）"})
        return {"source": "socialscan", "available": False, "error": "socialscan 未安装", "registered": []}

    await _emit(emit, "backend_start", {"name": "socialscan", "modules": "all"})

    def _run():
        try:
            return sync_execute_queries([email], Platforms)
        except Exception as exc:
            return exc

    outcome = await asyncio.to_thread(_run)
    if isinstance(outcome, Exception):
        await _emit(emit, "backend_done", {"name": "socialscan", "error": str(outcome)})
        return {"source": "socialscan", "available": True, "error": str(outcome), "registered": []}

    registered = []
    for item in outcome or []:
        available = getattr(item, "available", None)
        success = getattr(item, "success", False)
        platform = str(getattr(item, "platform", item))
        if success and available is False:
            registered.append({
                "source": "socialscan",
                "title": platform,
                "status": "registered",
                "detail": getattr(item, "message", None) or "socialscan: 邮箱不可用（通常表示已占用）",
            })
            await _emit(emit, "result", {
                "provider": f"socialscan_{platform}",
                "title": f"[Socialscan] {platform}",
                "category": "social",
                "homepage": None,
                "status": "registered",
                "detail": "socialscan 判定邮箱已被占用",
                "elapsed_ms": 0,
                "http_status": None,
                "data": {},
            })

    await _emit(emit, "backend_done", {"name": "socialscan", "registered_count": len(registered)})
    return {"source": "socialscan", "available": True, "registered": registered}


def _strip_tags(html: str) -> str:
    text = re.sub(r"(?is)<script.*?>.*?</script>", " ", html)
    text = re.sub(r"(?is)<style.*?>.*?</style>", " ", text)
    text = re.sub(r"(?s)<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def compute_bundle_stats(bundle: dict[str, Any]) -> dict[str, Any]:
    backends = bundle.get("backends") or {}
    seek = backends.get("seek_rules") or {}
    holehe = backends.get("holehe") or {}
    gravatar = backends.get("gravatar") or {}

    registered = len(bundle.get("merged_registered") or [])
    intel = len(seek.get("info") or [])
    not_reg = int(seek.get("not_registered_count") or 0) + int(holehe.get("not_registered_count") or 0)
    if gravatar.get("registered") is False and not gravatar.get("error"):
        not_reg += 1
    failed = int(seek.get("failed_or_unknown_count") or 0) + int(holehe.get("failed_or_unknown_count") or 0)
    checked = int(seek.get("total") or 0) + int(holehe.get("total") or 0)
    if gravatar and not gravatar.get("error"):
        checked += 1
    effective = registered + intel + not_reg
    return {
        "profile": bundle.get("profile") or "reliable",
        "checked": checked,
        "registered": registered,
        "intel": intel,
        "not_registered": not_reg,
        "failed": failed,
        "effective": effective,
        "web_hits": len((backends.get("web_search") or {}).get("results") or []),
    }


async def run_all_backends(
    email: str,
    settings: Settings,
    emit: Emit | None = None,
    profile: str | None = None,
) -> dict[str, Any]:
    """按档位并行跑后端，返回聚合证据包。"""
    profile = settings.normalize_profile(profile, kind="ai")
    backends = ["seek_rules", "gravatar", "web_search", "socialscan"]
    if profile == "full":
        backends.insert(1, "holehe")

    await _emit(emit, "aggregate_start", {
        "email": email,
        "profile": profile,
        "backends": backends,
    })

    tasks: list[asyncio.Task] = [
        asyncio.create_task(run_seek_rules(email, settings, emit, profile=profile)),
        asyncio.create_task(run_gravatar(email, settings, emit)),
        asyncio.create_task(run_web_searches(email, settings, emit)),
        asyncio.create_task(run_socialscan(email, settings, emit)),
    ]
    names = ["seek_rules", "gravatar", "web_search", "socialscan"]
    if profile == "full":
        tasks.insert(1, asyncio.create_task(run_holehe(email, settings, emit)))
        names.insert(1, "holehe")

    outcomes = await asyncio.gather(*tasks, return_exceptions=True)

    def ok(value: Any, name: str) -> dict[str, Any]:
        if isinstance(value, Exception):
            log.exception("后端 %s 失败", name)
            return {"source": name, "error": f"{type(value).__name__}: {value}"}
        return value

    backend_map = {name: ok(val, name) for name, val in zip(names, outcomes)}
    if profile != "full":
        backend_map["holehe"] = {
            "source": "holehe",
            "available": False,
            "skipped": True,
            "reason": "可靠模式默认跳过 Holehe（噪声高）。完整模式可设 SEEK_AI_PROFILE=full",
            "registered": [],
            "info": [],
        }

    bundle: dict[str, Any] = {
        "email": email,
        "profile": profile,
        "backends": backend_map,
    }

    merged: dict[str, dict[str, Any]] = {}
    for key in ("seek_rules", "holehe", "socialscan"):
        block = bundle["backends"].get(key) or {}
        for item in block.get("registered") or []:
            title = (item.get("title") or item.get("provider") or "").strip()
            if not title:
                continue
            merged.setdefault(title.lower(), item)
    if (bundle["backends"].get("gravatar") or {}).get("registered"):
        g = bundle["backends"]["gravatar"]
        merged["gravatar"] = {
            "source": "gravatar",
            "title": "Gravatar",
            "status": "registered",
            "detail": "存在公开资料/头像",
            "data": g.get("profile") or {},
            "homepage": "https://gravatar.com",
        }

    bundle["merged_registered"] = list(merged.values())
    bundle["stats"] = compute_bundle_stats(bundle)
    await _emit(emit, "aggregate_done", {
        "profile": profile,
        "merged_registered_count": len(bundle["merged_registered"]),
        "stats": bundle["stats"],
        "backends_ok": [k for k, v in bundle["backends"].items() if not v.get("error") and not v.get("skipped")],
    })
    return bundle


def bundle_for_llm(bundle: dict[str, Any]) -> str:
    """压缩成给大模型的证据文本（控制 token）。"""
    seek = (bundle.get("backends") or {}).get("seek_rules") or {}
    holehe = (bundle.get("backends") or {}).get("holehe") or {}
    slim = {
        "email": bundle.get("email"),
        "profile": bundle.get("profile"),
        "stats": bundle.get("stats") or compute_bundle_stats(bundle),
        "merged_registered": bundle.get("merged_registered") or [],
        "intel": seek.get("info") or [],
        "not_registered_sample": (seek.get("not_registered") or [])[:25],
        "gravatar": bundle.get("backends", {}).get("gravatar"),
        "web_search_top": (bundle.get("backends", {}).get("web_search") or {}).get("results", [])[:12],
        "seek_counts": {
            "total": seek.get("total"),
            "registered": len(seek.get("registered") or []),
            "not_registered": seek.get("not_registered_count"),
            "failed": seek.get("failed_or_unknown_count"),
        },
        "holehe_counts": {
            "skipped": bool(holehe.get("skipped")),
            "total": holehe.get("total"),
            "registered": len(holehe.get("registered") or []),
            "not_registered": holehe.get("not_registered_count"),
            "failed": holehe.get("failed_or_unknown_count"),
        },
        "notes": [
            "stats.effective = 已注册 + 情报 + 未注册（有效判定）；不是失败",
            "confirmed 为空也可能正常：该邮箱确实未在已测站点注册",
            "intel 必须写入域名 MX / 邮箱服务商等信息",
            "failed/unknown 不代表未注册，也不代表网站坏了",
        ],
    }
    return json.dumps(slim, ensure_ascii=False, indent=2)[:14000]


def enrich_report(report: dict[str, Any], bundle: dict[str, Any]) -> dict[str, Any]:
    """用聚合结果补全报告字段，保证前端始终有可用看板。"""
    stats = bundle.get("stats") or compute_bundle_stats(bundle)
    seek = (bundle.get("backends") or {}).get("seek_rules") or {}

    intel = list(report.get("intel") or [])
    if not intel:
        for item in seek.get("info") or []:
            intel.append({
                "site": item.get("title") or item.get("provider"),
                "evidence": item.get("detail") or "域名/邮箱情报",
                "url": item.get("homepage") or "",
                "source": item.get("source") or "seek_rules",
            })

    not_reg = list(report.get("not_registered") or [])
    if not not_reg:
        for item in (seek.get("not_registered") or [])[:20]:
            not_reg.append({
                "site": item.get("title"),
                "evidence": item.get("detail") or "工具明确判定未注册",
                "url": item.get("homepage") or "",
                "source": item.get("source") or "seek_rules",
            })
        g = (bundle.get("backends") or {}).get("gravatar") or {}
        if g.get("registered") is False and not g.get("error"):
            not_reg.insert(0, {
                "site": "Gravatar",
                "evidence": "无公开 Gravatar 资料",
                "url": "https://gravatar.com",
                "source": "gravatar",
            })

    confirmed = list(report.get("confirmed") or [])
    if not confirmed:
        for item in bundle.get("merged_registered") or []:
            confirmed.append({
                "site": item.get("title") or item.get("provider"),
                "evidence": item.get("detail") or f"来源 {item.get('source')}",
                "url": item.get("homepage") or "",
                "source": item.get("source"),
            })

    summary = (report.get("summary") or "").strip()
    if not summary:
        summary = (
            f"可靠检测完成：有效判定 {stats.get('effective', 0)} 项"
            f"（已注册 {stats.get('registered', 0)} / 未注册 {stats.get('not_registered', 0)} / 情报 {stats.get('intel', 0)}）。"
            f"已注册为空通常表示在已测站点未发现账号，不等于工具失效。"
        )
    elif stats.get("registered", 0) == 0 and "失效" not in summary and "坏了" not in summary:
        # 避免模型把「无命中」写成「工具没用」
        if "未发现" not in summary and "没有确认" not in summary and "暂无" not in summary:
            summary = summary.rstrip("。") + "。已注册为空不一定是故障，也可能是邮箱确实未注册。"

    report.update({
        "summary": summary,
        "confirmed": confirmed,
        "likely": report.get("likely") or [],
        "intel": intel,
        "not_registered": not_reg,
        "unchecked_or_failed": report.get("unchecked_or_failed") or [
            f"{x.get('title')}: {x.get('status')}"
            for x in (seek.get("failed_or_unknown") or [])[:15]
        ],
        "next_steps": report.get("next_steps") or [
            "在 https://haveibeenpwned.com 免费手查泄露记录",
            "对关心的站点打开官网登录页人工核对",
            "需要更广覆盖可在 .env 设 SEEK_AI_PROFILE=full 后重启（噪声会明显增加）",
        ],
        "stats": stats,
        "profile": bundle.get("profile") or stats.get("profile"),
        "backends": {
            k: {
                "error": v.get("error"),
                "available": v.get("available", True),
                "skipped": v.get("skipped", False),
                "registered_count": len(v.get("registered") or []),
                "not_registered_count": v.get("not_registered_count"),
                "failed_or_unknown_count": v.get("failed_or_unknown_count"),
                "effective_count": v.get("effective_count"),
            }
            for k, v in ((bundle.get("backends") or {}).items())
            if isinstance(v, dict)
        },
    })
    return report
