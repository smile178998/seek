from __future__ import annotations

import asyncio
import time
from pathlib import Path

import dns.asyncresolver
import dns.exception
import dns.resolver
import httpx

from ...models import ProviderInfo, Result, Status
from ...utils import split_email
from ..base import CheckContext, Provider, Timer
from . import register

DATA_DIR = Path(__file__).resolve().parents[2] / "data"
MX_CACHE_TTL = 300.0
DOH_ENDPOINT = "https://dns.alidns.com/resolve"
_mx_cache: dict[str, tuple[float, tuple[list[str], bool]]] = {}
_mx_inflight: dict[str, asyncio.Task[tuple[list[str], bool]]] = {}

# MX 主机名特征 -> 邮箱服务商
MX_FINGERPRINTS: list[tuple[str, str]] = [
    ("google.com", "Google Workspace / Gmail"),
    ("googlemail.com", "Google Workspace / Gmail"),
    ("outlook.com", "Microsoft 365 / Outlook"),
    ("protection.outlook.com", "Microsoft 365"),
    ("qq.com", "腾讯邮箱"),
    ("exmail.qq.com", "腾讯企业邮"),
    ("163.com", "网易邮箱"),
    ("126.com", "网易邮箱"),
    ("qiye.163.com", "网易企业邮"),
    ("aliyun.com", "阿里云邮箱"),
    ("mxhichina.com", "阿里云企业邮"),
    ("feishu.cn", "飞书邮箱"),
    ("zoho.com", "Zoho Mail"),
    ("zohomail", "Zoho Mail"),
    ("yandex", "Yandex Mail"),
    ("protonmail.ch", "Proton Mail"),
    ("proton.me", "Proton Mail"),
    ("icloud.com", "iCloud Mail"),
    ("me.com", "iCloud Mail"),
    ("messagingengine.com", "Fastmail"),
    ("mimecast.com", "Mimecast（企业网关）"),
    ("pphosted.com", "Proofpoint（企业网关）"),
    ("barracudanetworks.com", "Barracuda（企业网关）"),
    ("secureserver.net", "GoDaddy"),
    ("yahoodns.net", "Yahoo Mail"),
    ("sendgrid.net", "SendGrid"),
]


def _mx_records(answers) -> tuple[list[str], bool]:
    records = sorted(
        (
            (int(record.preference), str(record.exchange).rstrip(".").lower())
            for record in answers
        ),
        key=lambda item: item[0],
    )
    hosts = [host for _preference, host in records if host]
    return hosts, bool(records) and not hosts


async def _query_mx_doh(
    domain: str,
    client: httpx.AsyncClient,
) -> tuple[list[str], bool]:
    """在本地 UDP DNS 不可用时通过 HTTPS 查询 MX。"""
    try:
        response = await client.get(
            DOH_ENDPOINT,
            params={"name": domain, "type": "MX"},
            headers={"Accept": "application/dns-json"},
            timeout=8.0,
        )
        response.raise_for_status()
        payload = response.json()
    except (httpx.HTTPError, ValueError) as exc:
        raise dns.exception.DNSException(f"HTTPS DNS 查询失败: {exc}") from exc

    status = int(payload.get("Status", -1))
    if status == 3:
        raise dns.resolver.NXDOMAIN
    if status != 0:
        raise dns.exception.DNSException(f"HTTPS DNS 返回状态 {status}")

    records: list[tuple[int, str]] = []
    for answer in payload.get("Answer") or []:
        if int(answer.get("type", 0)) != 15:
            continue
        parts = str(answer.get("data") or "").strip().split(maxsplit=1)
        if len(parts) != 2:
            continue
        records.append((int(parts[0]), parts[1].strip('"').rstrip(".").lower()))
    if not records:
        raise dns.resolver.NoAnswer
    records.sort(key=lambda item: item[0])
    hosts = [host for _preference, host in records if host]
    return hosts, bool(records) and not hosts


async def _query_mx(
    domain: str,
    client: httpx.AsyncClient,
) -> tuple[list[str], bool]:
    """返回 (按优先级排序的 MX 主机, 是否为 Null MX)。

    Null MX（RFC 7505）是一条 exchange 为 "." 的记录，表示该域名明确不接收邮件。
    """
    resolver = dns.asyncresolver.Resolver()
    resolver.lifetime = 6.0
    try:
        answers = await resolver.resolve(domain, "MX")
    except dns.exception.Timeout:
        # 公共 UDP DNS 在部分公司/容器网络也会被拦，因此回退到 DoH。
        return await _query_mx_doh(domain, client)
    return _mx_records(answers)


async def _resolve_mx(
    domain: str,
    client: httpx.AsyncClient,
) -> tuple[list[str], bool]:
    """合并同一域名的并发查询并短期缓存，避免 MX 与邮箱服务商模块重复压垮 DNS。"""
    key = domain.strip().lower()
    now = time.monotonic()
    cached = _mx_cache.get(key)
    if cached and now - cached[0] < MX_CACHE_TTL:
        return cached[1]

    task = _mx_inflight.get(key)
    if task is None:
        task = asyncio.create_task(_query_mx(key, client))
        _mx_inflight[key] = task
    try:
        result = await task
        _mx_cache[key] = (time.monotonic(), result)
        return result
    finally:
        if _mx_inflight.get(key) is task:
            _mx_inflight.pop(key, None)


class MxProvider(Provider):
    """判断邮箱域名是否具备收信能力（公开 DNS 记录）。"""

    def __init__(self) -> None:
        super().__init__(
            ProviderInfo(
                name="mx",
                title="域名 MX 记录",
                category="domain",
                description="通过公开 DNS 判断该邮箱域名能否接收邮件",
                kind="builtin",
            )
        )

    async def check(self, ctx: CheckContext) -> Result:
        _local, domain = split_email(ctx.email)
        with Timer() as timer:
            try:
                hosts, null_mx = await _resolve_mx(domain, ctx.client)
            except dns.resolver.NXDOMAIN:
                return self.make_result(
                    Status.NOT_REGISTERED,
                    elapsed_ms=timer.ms,
                    detail=f"域名 {domain} 不存在",
                )
            except dns.resolver.NoAnswer:
                return self.make_result(
                    Status.NOT_REGISTERED,
                    elapsed_ms=timer.ms,
                    detail=f"{domain} 没有 MX 记录，无法收信",
                )
            except dns.exception.DNSException as exc:
                return self.make_result(
                    Status.ERROR, elapsed_ms=timer.ms, detail=f"DNS 查询失败: {exc}"
                )

        if null_mx:
            return self.make_result(
                Status.NOT_REGISTERED,
                elapsed_ms=timer.elapsed_ms,
                detail=f"{domain} 配置了 Null MX，明确声明不接收邮件",
            )
        return self.make_result(
            Status.INFO,
            elapsed_ms=timer.elapsed_ms,
            detail=f"{domain} 可正常收信，共 {len(hosts)} 条 MX 记录",
            data={"mx": hosts[:5]},
        )


class MailProviderProvider(Provider):
    """从 MX 记录反推邮箱背后的服务商。"""

    def __init__(self) -> None:
        super().__init__(
            ProviderInfo(
                name="mail_provider",
                title="邮件服务商识别",
                category="domain",
                description="根据 MX 指纹推断邮箱使用的服务商 / 邮件网关",
                kind="builtin",
            )
        )

    async def check(self, ctx: CheckContext) -> Result:
        _local, domain = split_email(ctx.email)
        with Timer() as timer:
            try:
                hosts, null_mx = await _resolve_mx(domain, ctx.client)
            except dns.exception.DNSException as exc:
                return self.make_result(
                    Status.ERROR, elapsed_ms=timer.ms, detail=f"DNS 查询失败: {exc}"
                )

        if null_mx or not hosts:
            return self.make_result(
                Status.NOT_REGISTERED,
                elapsed_ms=timer.elapsed_ms,
                detail="该域名没有可用的 MX 记录",
            )

        matched = sorted(
            {label for host in hosts for needle, label in MX_FINGERPRINTS if needle in host}
        )
        if not matched:
            return self.make_result(
                Status.UNKNOWN,
                elapsed_ms=timer.elapsed_ms,
                detail="未匹配到已知服务商指纹（可能为自建邮件服务器）",
                data={"mx": hosts[:5]},
            )
        return self.make_result(
            Status.INFO,
            elapsed_ms=timer.elapsed_ms,
            detail="、".join(matched),
            data={"providers": matched, "mx": hosts[:5]},
        )


class DisposableProvider(Provider):
    """判断是否为一次性 / 临时邮箱域名。"""

    def __init__(self) -> None:
        super().__init__(
            ProviderInfo(
                name="disposable",
                title="一次性邮箱识别",
                category="domain",
                description="比对本地临时邮箱域名库",
                kind="builtin",
            )
        )
        self._domains = self._load()

    @staticmethod
    def _load() -> set[str]:
        path = DATA_DIR / "disposable_domains.txt"
        if not path.exists():
            return set()
        lines = path.read_text(encoding="utf-8").splitlines()
        return {
            line.strip().lower()
            for line in lines
            if line.strip() and not line.startswith("#")
        }

    async def check(self, ctx: CheckContext) -> Result:
        _local, domain = split_email(ctx.email)
        if not self._domains:
            return self.make_result(Status.SKIPPED, detail="本地域名库为空")
        if domain.lower() in self._domains:
            return self.make_result(
                Status.INFO, detail=f"{domain} 属于一次性邮箱服务", data={"disposable": True}
            )
        return self.make_result(
            Status.NOT_REGISTERED,
            detail="不在已知一次性邮箱域名库中",
            data={"disposable": False},
        )


@register
def _mx() -> Provider:
    return MxProvider()


@register
def _mail_provider() -> Provider:
    return MailProviderProvider()


@register
def _disposable() -> Provider:
    return DisposableProvider()
