from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path

from dotenv import dotenv_values
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent
PACKAGE_DIR = Path(__file__).resolve().parent

DEFAULT_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_prefix="SEEK_",
        extra="ignore",
        env_file_encoding="utf-8",
    )

    host: str = "127.0.0.1"
    port: int = 8000

    concurrency: int = 12
    timeout: float = 12.0
    user_agent: str = DEFAULT_USER_AGENT
    proxy: str | None = None

    # 被禁用的 holehe 模块清单文件（一行一个模块名，# 开头为注释）
    holehe_disabled_file: Path = PACKAGE_DIR / "data" / "holehe_disabled.txt"
    # 可靠模块白名单（一行一个模块名）
    reliable_modules_file: Path = PACKAGE_DIR / "data" / "reliable_modules.txt"
    # 规则扫描默认档位：reliable（只跑白名单）| full（全部已启用规则）
    scan_profile: str = "reliable"
    # AI 聚合默认档位：reliable（白名单 + Gravatar/搜索，不跑 Holehe）| full（含 Holehe）
    ai_profile: str = "reliable"

    # SSL 证书校验。默认 True 并优先使用系统证书库（truststore），可识别杀软 / 企业
    # 网关注入的本地 CA，避免大量站点因 TLS 拦截而握手失败。设为 false 可完全关闭校验。
    ssl_verify: bool = True

    # 逗号分隔；留空表示不限制被查询的邮箱域名
    allowed_domains: str = ""
    require_consent: bool = True
    rate_limit_scans: int = 12
    rate_limit_window: int = 600

    definitions_dir: Path = PACKAGE_DIR / "definitions"
    web_dir: Path = BASE_DIR / "web"

    @property
    def domain_allowlist(self) -> set[str]:
        return {d.strip().lower() for d in self.allowed_domains.split(",") if d.strip()}

    def is_domain_allowed(self, domain: str) -> bool:
        allow = self.domain_allowlist
        return not allow or domain.lower() in allow

    def disabled_holehe(self) -> set[str]:
        """读取被禁用的 holehe 模块名集合（归一化为不带 holehe_ 前缀的小写名）。"""
        return self._read_name_set(self.holehe_disabled_file, strip_prefix="holehe_")

    def reliable_modules(self) -> set[str]:
        """可靠模式白名单模块名（小写）。"""
        return self._read_name_set(self.reliable_modules_file)

    @staticmethod
    def _read_name_set(path: Path, strip_prefix: str | None = None) -> set[str]:
        if not path.exists():
            return set()
        names: set[str] = set()
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            name = line.lower()
            if strip_prefix and name.startswith(strip_prefix):
                name = name[len(strip_prefix) :]
            names.add(name)
        return names

    def normalize_profile(self, profile: str | None, *, kind: str = "scan") -> str:
        value = (profile or (self.ai_profile if kind == "ai" else self.scan_profile) or "reliable")
        value = value.strip().lower()
        return value if value in ("reliable", "full") else "reliable"


@lru_cache
def get_settings() -> Settings:
    return Settings()


def build_ssl_verify(settings: "Settings"):
    """返回传给 httpx 的 verify 值。

    - ssl_verify=False -> 关闭校验（返回 False）
    - 否则优先用 truststore 走系统证书库（能认到杀软 / 企业网关的本地 CA）
    - truststore 不可用时回退到 certifi（返回 True）
    """
    if not settings.ssl_verify:
        return False
    try:
        import ssl

        import truststore

        return truststore.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    except Exception:
        return True


@lru_cache
def get_secrets() -> dict[str, str]:
    """规则里 `{env.XXX}` 可引用的变量：.env 文件 + 进程环境变量。"""
    values: dict[str, str] = {
        k: v for k, v in dotenv_values(BASE_DIR / ".env").items() if v is not None
    }
    values.update({k: v for k, v in os.environ.items() if v})
    return values


def lookup_secret(key: str) -> str | None:
    """支持 `HIBP_API_KEY` 与 `SEEK_HIBP_API_KEY` 两种写法。"""
    secrets = get_secrets()
    for candidate in (key, f"SEEK_{key}", key.upper(), f"SEEK_{key.upper()}"):
        value = secrets.get(candidate)
        if value:
            return value
    return None
