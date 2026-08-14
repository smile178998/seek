from __future__ import annotations

import abc
import time
from dataclasses import dataclass
from typing import Any

import httpx

from ..models import ProviderInfo, Result, Status


@dataclass
class CheckContext:
    """单次检测所需的运行时依赖。"""

    email: str
    client: httpx.AsyncClient
    timeout: float


class Provider(abc.ABC):
    """所有检测模块的基类。"""

    def __init__(self, info: ProviderInfo) -> None:
        self.info = info

    @property
    def name(self) -> str:
        return self.info.name

    def execution_timeout(self, ctx: CheckContext) -> float:
        """Return the scheduler's wall-clock budget for this provider."""
        return ctx.timeout + 2.0

    @abc.abstractmethod
    async def check(self, ctx: CheckContext) -> Result:  # pragma: no cover - 接口定义
        ...

    def make_result(
        self,
        status: Status,
        *,
        elapsed_ms: int = 0,
        http_status: int | None = None,
        detail: str | None = None,
        data: dict[str, Any] | None = None,
    ) -> Result:
        return Result(
            provider=self.info.name,
            title=self.info.title,
            category=self.info.category,
            homepage=self.info.homepage,
            status=status,
            elapsed_ms=elapsed_ms,
            http_status=http_status,
            detail=detail,
            data=data or {},
        )


class Timer:
    """记录耗时（毫秒）。"""

    def __enter__(self) -> "Timer":
        self._start = time.perf_counter()
        self.elapsed_ms = 0
        return self

    def __exit__(self, *_exc: object) -> None:
        self.elapsed_ms = int((time.perf_counter() - self._start) * 1000)

    @property
    def ms(self) -> int:
        return int((time.perf_counter() - self._start) * 1000)
