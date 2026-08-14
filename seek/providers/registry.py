from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

import yaml

from ..config import Settings, get_settings
from .base import Provider
from .builtin import BUILTIN_FACTORIES
from .declarative import DeclarativeProvider, build_provider_info
from .holehe_bridge import load_holehe_providers

log = logging.getLogger(__name__)


def _site_key(name: str) -> str:
    """归一化站点名，用于去掉 YAML 与 Holehe 的重复模块。"""
    return "".join(char for char in name.lower() if char.isalnum())


def load_definition_files(directory: Path) -> list[tuple[Path, dict[str, Any]]]:
    specs: list[tuple[Path, dict[str, Any]]] = []
    if not directory.exists():
        log.warning("规则目录不存在: %s", directory)
        return specs
    for path in sorted(directory.glob("*.y*ml")):
        try:
            spec = yaml.safe_load(path.read_text(encoding="utf-8"))
        except yaml.YAMLError as exc:
            log.error("规则文件解析失败 %s: %s", path.name, exc)
            continue
        if not isinstance(spec, dict):
            log.error("规则文件格式不正确（顶层需为映射）: %s", path.name)
            continue
        specs.append((path, spec))
    return specs


def load_providers(
    settings: Settings | None = None,
    profile: str | None = None,
    include_holehe: bool | None = None,
) -> list[Provider]:
    """加载检测模块：内置 Python 模块 + definitions 目录下的 YAML 规则。

    - profile=reliable（默认）：只保留白名单高可用模块，减少 unknown/失败噪声。
    - profile=full：加载全部 YAML 规则，并按需接入 Holehe 的上百个站点模块（覆盖最大，噪声更大）。

    include_holehe 为 None 时会接入 Holehe：full 档保留所有未禁用模块，
    reliable 档只保留 reliable_modules_file 白名单中的模块。
    """
    settings = settings or get_settings()
    profile = settings.normalize_profile(profile, kind="scan")
    if include_holehe is None:
        # reliable 档也会加载 Holehe，但最后只保留白名单中经过筛选的模块。
        # Holehe 未安装时 load_holehe_providers() 返回空列表，不影响自维护规则。
        include_holehe = True

    providers: list[Provider] = [factory() for factory in BUILTIN_FACTORIES]
    definition_files = load_definition_files(settings.definitions_dir)
    definition_keys = {
        _site_key(str(spec.get("name") or path.stem))
        for path, spec in definition_files
        if spec.get("enabled", True) and "request" in spec
    }

    if include_holehe:
        disabled = settings.disabled_holehe()
        for provider in load_holehe_providers():
            short = provider.info.name
            if short.startswith("holehe_"):
                short = short[len("holehe_") :]
            if short in disabled or _site_key(short) in definition_keys:
                continue
            providers.append(provider)
        if disabled:
            log.info("已按禁用清单跳过 %d 个 holehe 模块", len(disabled))

    for path, spec in definition_files:
        info = build_provider_info(spec, path.stem)
        if not info.enabled:
            log.debug("规则已禁用，跳过: %s", info.name)
            continue
        if "request" not in spec:
            log.error("规则缺少 request 段: %s", path.name)
            continue
        providers.append(DeclarativeProvider(info, spec))

    if profile == "reliable":
        allow = settings.reliable_modules()
        if allow:
            before = len(providers)
            providers = [p for p in providers if p.info.name.lower() in allow]
            log.info("可靠模式：%d/%d 个模块", len(providers), before)

    providers.sort(key=lambda p: (p.info.category, p.info.name))
    return providers


def filter_providers(
    providers: list[Provider],
    only: list[str] | None = None,
    exclude: list[str] | None = None,
) -> list[Provider]:
    selected = providers
    if only:
        wanted = {n.strip().lower() for n in only if n.strip()}
        selected = [
            p
            for p in selected
            if p.info.name.lower() in wanted or p.info.category.lower() in wanted
        ]
    if exclude:
        unwanted = {n.strip().lower() for n in exclude if n.strip()}
        selected = [
            p
            for p in selected
            if p.info.name.lower() not in unwanted
            and p.info.category.lower() not in unwanted
        ]
    return selected
