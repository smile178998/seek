from __future__ import annotations

import time
from collections import deque


class SlidingWindowLimiter:
    """进程内滑动窗口限流器（单机足够；多实例部署请换 Redis）。"""

    def __init__(self, limit: int, window_seconds: int, max_keys: int = 10_000) -> None:
        self.limit = limit
        self.window = window_seconds
        self.max_keys = max_keys
        self._hits: dict[str, deque[float]] = {}

    def check(self, key: str) -> tuple[bool, int]:
        """返回 (是否允许, 需要等待的秒数)。"""
        if self.limit <= 0:
            return True, 0
        now = time.monotonic()
        if key not in self._hits and len(self._hits) >= self.max_keys:
            self._prune(now)
            if len(self._hits) >= self.max_keys:
                self._hits.pop(next(iter(self._hits)))
        bucket = self._hits.setdefault(key, deque())
        while bucket and now - bucket[0] > self.window:
            bucket.popleft()
        if len(bucket) >= self.limit:
            retry_after = int(self.window - (now - bucket[0])) + 1
            return False, max(retry_after, 1)
        bucket.append(now)
        return True, 0

    def remaining(self, key: str) -> int:
        if self.limit <= 0:
            return -1
        now = time.monotonic()
        bucket = self._hits.get(key)
        if not bucket:
            return self.limit
        while bucket and now - bucket[0] > self.window:
            bucket.popleft()
        if not bucket:
            self._hits.pop(key, None)
        return max(0, self.limit - len(bucket))

    def _prune(self, now: float) -> None:
        expired = [
            key
            for key, bucket in self._hits.items()
            if not bucket or now - bucket[-1] > self.window
        ]
        for key in expired:
            self._hits.pop(key, None)
