from __future__ import annotations

import asyncio
import logging
import time
from typing import AsyncIterator, Sequence

import httpx

from .config import Settings, build_ssl_verify, get_settings
from .models import Result, ScanResponse, ScanSummary, Status
from .providers.base import CheckContext, Provider
from .providers.registry import filter_providers, load_providers

log = logging.getLogger(__name__)


class Engine:
    """并发调度所有检测模块。"""

    def __init__(
        self,
        providers: Sequence[Provider] | None = None,
        settings: Settings | None = None,
        transport: httpx.AsyncBaseTransport | None = None,
    ) -> None:
        self.settings = settings or get_settings()
        self.providers = list(providers) if providers is not None else load_providers(self.settings)
        self._transport = transport  # 仅用于测试时注入假响应
        self._client: httpx.AsyncClient | None = None

    # ---------- 生命周期 ----------
    async def __aenter__(self) -> "Engine":
        self._client = httpx.AsyncClient(
            headers={
                "User-Agent": self.settings.user_agent,
                "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            },
            proxy=self.settings.proxy or None,
            timeout=self.settings.timeout,
            limits=httpx.Limits(
                max_connections=self.settings.concurrency * 2,
                max_keepalive_connections=self.settings.concurrency,
            ),
            transport=self._transport,
            verify=build_ssl_verify(self.settings),
        )
        return self

    async def __aexit__(self, *_exc: object) -> None:
        if self._client is not None:
            await self._client.aclose()
            self._client = None

    @property
    def client(self) -> httpx.AsyncClient:
        if self._client is None:
            raise RuntimeError("Engine 需要在 async with 块内使用")
        return self._client

    # ---------- 扫描 ----------
    async def stream(
        self,
        email: str,
        only: list[str] | None = None,
        exclude: list[str] | None = None,
    ) -> AsyncIterator[Result]:
        """逐个产出结果，谁先返回就先产出。"""
        selected = filter_providers(self.providers, only, exclude)
        semaphore = asyncio.Semaphore(max(1, self.settings.concurrency))
        ctx = CheckContext(email=email, client=self.client, timeout=self.settings.timeout)
        hard_timeout = self.settings.timeout + 5

        async def run_one(provider: Provider) -> Result:
            if not provider.info.ready:
                return provider.make_result(
                    Status.SKIPPED, detail=provider.info.unready_reason or "模块未就绪"
                )
            async with semaphore:
                try:
                    return await asyncio.wait_for(provider.check(ctx), timeout=hard_timeout)
                except asyncio.TimeoutError:
                    return provider.make_result(Status.ERROR, detail="模块执行超时")
                except asyncio.CancelledError:
                    raise
                except Exception as exc:  # 单个模块异常不影响整体
                    log.exception("模块 %s 执行失败", provider.name)
                    return provider.make_result(
                        Status.ERROR, detail=f"模块异常: {type(exc).__name__}: {exc}"
                    )

        tasks = [asyncio.create_task(run_one(p)) for p in selected]
        try:
            for finished in asyncio.as_completed(tasks):
                yield await finished
        finally:
            for task in tasks:
                if not task.done():
                    task.cancel()
            await asyncio.gather(*tasks, return_exceptions=True)

    async def scan(
        self,
        email: str,
        only: list[str] | None = None,
        exclude: list[str] | None = None,
    ) -> ScanResponse:
        started = time.perf_counter()
        results = [r async for r in self.stream(email, only, exclude)]
        results.sort(key=lambda r: (_STATUS_ORDER.get(r.status, 99), r.category, r.title))
        elapsed_ms = int((time.perf_counter() - started) * 1000)
        return ScanResponse(
            summary=ScanSummary.from_results(email, results, elapsed_ms),
            results=results,
        )


_STATUS_ORDER = {
    Status.REGISTERED: 0,
    Status.INFO: 1,
    Status.UNKNOWN: 2,
    Status.RATE_LIMITED: 3,
    Status.NOT_REGISTERED: 4,
    Status.ERROR: 5,
    Status.SKIPPED: 6,
}
