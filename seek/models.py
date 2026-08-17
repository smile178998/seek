from __future__ import annotations

import enum
from typing import Any, Literal

from pydantic import BaseModel, Field


class Status(str, enum.Enum):
    REGISTERED = "registered"
    NOT_REGISTERED = "not_registered"
    INFO = "info"
    UNKNOWN = "unknown"
    RATE_LIMITED = "rate_limited"
    ERROR = "error"
    SKIPPED = "skipped"


STATUS_LABEL: dict[Status, str] = {
    Status.REGISTERED: "已注册",
    Status.NOT_REGISTERED: "未注册",
    Status.INFO: "情报",
    Status.UNKNOWN: "无法判定",
    Status.RATE_LIMITED: "被限流",
    Status.ERROR: "请求失败",
    Status.SKIPPED: "已跳过",
}


class ProviderInfo(BaseModel):
    name: str
    title: str
    category: str = "other"
    homepage: str | None = None
    description: str | None = None
    notes: str | None = None
    requires: list[str] = Field(default_factory=list)
    kind: Literal["declarative", "builtin"] = "declarative"
    enabled: bool = True
    ready: bool = True
    unready_reason: str | None = None


class Result(BaseModel):
    provider: str
    title: str
    category: str = "other"
    homepage: str | None = None
    status: Status = Status.UNKNOWN
    elapsed_ms: int = 0
    http_status: int | None = None
    detail: str | None = None
    data: dict[str, Any] = Field(default_factory=dict)


class ScanSummary(BaseModel):
    email: str
    total: int
    registered: int
    not_registered: int
    info: int
    unknown: int
    rate_limited: int
    error: int
    skipped: int
    elapsed_ms: int

    @classmethod
    def from_results(cls, email: str, results: list[Result], elapsed_ms: int) -> "ScanSummary":
        def count(status: Status) -> int:
            return sum(1 for r in results if r.status is status)

        return cls(
            email=email,
            total=len(results),
            registered=count(Status.REGISTERED),
            not_registered=count(Status.NOT_REGISTERED),
            info=count(Status.INFO),
            unknown=count(Status.UNKNOWN),
            rate_limited=count(Status.RATE_LIMITED),
            error=count(Status.ERROR),
            skipped=count(Status.SKIPPED),
            elapsed_ms=elapsed_ms,
        )


class ScanRequest(BaseModel):
    email: str
    consent: bool = False
    only: list[str] = Field(default_factory=list)
    exclude: list[str] = Field(default_factory=list)
    profile: Literal["reliable", "full"] | None = None


class AIInvestigateRequest(BaseModel):
    email: str
    consent: bool = False
    lang: Literal["zh", "en"] = "zh"


class ScanResponse(BaseModel):
    summary: ScanSummary
    results: list[Result]
