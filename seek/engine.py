from __future__ import annotations

import asyncio
import logging
import time
from typing import AsyncIterator, Sequence

import httpx

from .config import Settings, build_ssl_verify, get_settings
from .models import Result, ScanResponse, ScanSummary, Status
from .providers.base import CheckContext, PhoneCheckContext, Provider
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
        category_semaphores = {"adult": asyncio.Semaphore(1)}
        ctx = CheckContext(email=email, client=self.client, timeout=self.settings.timeout)
        # 网络层已有单请求超时；仅留少量清理余量，避免慢模块拖住整批扫描。
        def detach(task: asyncio.Task[Result]) -> None:
            """取消慢模块但不等待其连接清理，保证结果流按时结束。"""
            task.cancel()

            def consume(done: asyncio.Task[Result]) -> None:
                try:
                    done.exception()
                except (asyncio.CancelledError, Exception):
                    pass

            task.add_done_callback(consume)

        async def execute(provider: Provider) -> Result:
            try:
                check_task = asyncio.create_task(provider.check(ctx))
                done, _ = await asyncio.wait(
                    {check_task}, timeout=provider.execution_timeout(ctx)
                )
                if not done:
                    detach(check_task)
                    return provider.make_result(Status.ERROR, detail="模块执行超时")
                return await check_task
            except asyncio.TimeoutError:  # 兼容模块内部主动抛出的超时
                return provider.make_result(Status.ERROR, detail="模块执行超时")
            except asyncio.CancelledError:
                raise
            except Exception as exc:  # 单个模块异常不影响整体
                log.exception("模块 %s 执行失败", provider.name)
                return provider.make_result(
                    Status.ERROR, detail=f"模块异常: {type(exc).__name__}: {exc}"
                )

        async def run_one(provider: Provider) -> Result:
            if not provider.info.ready:
                return provider.make_result(
                    Status.SKIPPED, detail=provider.info.unready_reason or "模块未就绪"
                )
            async with semaphore:
                category_semaphore = category_semaphores.get(provider.info.category)
                if category_semaphore is not None:
                    async with category_semaphore:
                        return await execute(provider)
                return await execute(provider)

        async def run_pair(provider: Provider) -> tuple[Provider, Result]:
            return provider, await run_one(provider)

        tasks = [asyncio.create_task(run_pair(p)) for p in selected]
        try:
            retryable: list[Provider] = []
            for finished in asyncio.as_completed(tasks):
                provider, result = await finished
                if _is_retryable_network_error(result):
                    retryable.append(provider)
                else:
                    yield result

            # Large batches can briefly exhaust DNS/TLS or remote connection
            # capacity. Retry only transient failures after the main wave has
            # drained, and use low concurrency for the retry wave.
            retry_semaphore = asyncio.Semaphore(1)

            async def retry_one(provider: Provider) -> tuple[Provider, Result]:
                async with retry_semaphore:
                    return await run_pair(provider)

            retry_tasks = [asyncio.create_task(retry_one(p)) for p in retryable]
            tasks.extend(retry_tasks)
            for finished in asyncio.as_completed(retry_tasks):
                _, result = await finished
                yield result
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

    async def scan_phone(
        self,
        phone: str,
        only: list[str] | None = None,
        exclude: list[str] | None = None,
    ) -> ScanResponse:
        started = time.perf_counter()
        results = [r async for r in self.stream_phone(phone, only, exclude)]
        results.sort(key=lambda r: (_STATUS_ORDER.get(r.status, 99), r.category, r.title))
        elapsed_ms = int((time.perf_counter() - started) * 1000)
        return ScanResponse(
            summary=ScanSummary.from_results(phone, results, elapsed_ms),
            results=results,
        )

    async def stream_phone(
        self,
        phone: str,
        only: list[str] | None = None,
        exclude: list[str] | None = None,
    ) -> AsyncIterator[Result]:
        selected = [
            provider
            for provider in filter_providers(self.providers, only, exclude)
            if provider.supports_phone
        ]
        semaphore = asyncio.Semaphore(max(1, self.settings.concurrency))
        ctx = PhoneCheckContext(phone=phone, client=self.client, timeout=self.settings.timeout)

        async def run(provider: Provider) -> Result:
            if not provider.info.ready:
                return provider.make_result(Status.SKIPPED, detail=provider.info.unready_reason or "模块未就绪")
            async with semaphore:
                try:
                    return await asyncio.wait_for(provider.check_phone(ctx), provider.execution_timeout(ctx))
                except asyncio.TimeoutError:
                    return provider.make_result(Status.ERROR, detail="模块执行超时")
                except Exception as exc:
                    return provider.make_result(Status.ERROR, detail=f"模块异常: {type(exc).__name__}: {exc}")

        tasks = [asyncio.create_task(run(provider)) for provider in selected]
        try:
            for finished in asyncio.as_completed(tasks):
                yield await finished
        finally:
            for task in tasks:
                if not task.done():
                    task.cancel()
            await asyncio.gather(*tasks, return_exceptions=True)


_STATUS_ORDER = {
    Status.REGISTERED: 0,
    Status.INFO: 1,
    Status.UNKNOWN: 2,
    Status.RATE_LIMITED: 3,
    Status.NOT_REGISTERED: 4,
    Status.ERROR: 5,
    Status.SKIPPED: 6,
}


def _is_retryable_network_error(result: Result) -> bool:
    if result.status is Status.RATE_LIMITED:
        return True
    if result.status is not Status.ERROR:
        return False
    detail = (result.detail or "").lower()
    markers = (
        "timeout",
        "timed out",
        "connecterror",
        "connection error",
        "network error",
        "proxyerror",
        "remoteprotocolerror",
        "http 408",
        "http 425",
        "http 483",
        "http 500",
        "http 502",
        "http 503",
        "http 504",
        "瓒呮椂",
        "缃戠粶",
        "超时",
        "网络",
    )
    return not detail or any(marker in detail for marker in markers)
