from __future__ import annotations

import time
from collections import defaultdict, deque


class SlidingWindowLimiter:
    """进程内滑动窗口限流器（单机足够；多实例部署请换 Redis）。"""

    def __init__(self, limit: int, window_seconds: int) -> None:
        self.limit = limit
        self.window = window_seconds
        self._hits: dict[str, deque[float]] = defaultdict(deque)

    def check(self, key: str) -> tuple[bool, int]:
        """返回 (是否允许, 需要等待的秒数)。"""
        if self.limit <= 0:
            return True, 0
        now = time.monotonic()
        bucket = self._hits[key]
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
        bucket = self._hits[key]
        while bucket and now - bucket[0] > self.window:
            bucket.popleft()
        return max(0, self.limit - len(bucket))
