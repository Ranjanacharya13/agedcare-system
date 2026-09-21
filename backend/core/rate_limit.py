"""Sliding-window rate limiting for unauthenticated endpoints."""

import time
from collections import defaultdict, deque

from fastapi import HTTPException, Request, status


class SlidingWindowLimiter:
    def __init__(self, max_requests: int, window_seconds: int):
        self._max = max_requests
        self._window = window_seconds
        self._hits: dict[str, deque[float]] = defaultdict(deque)

    def check(self, key: str) -> int | None:
        """Record a hit."""
        now = time.monotonic()
        hits = self._hits[key]
        while hits and now - hits[0] >= self._window:
            hits.popleft()
        if len(hits) >= self._max:
            return max(1, int(self._window - (now - hits[0])))
        hits.append(now)
        return None

    def reset(self) -> None:
        self._hits.clear()


def client_ip(request: Request) -> str:
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


def rate_limit_dependency(limiter: SlidingWindowLimiter):
    async def _check(request: Request) -> None:
        retry_after = limiter.check(client_ip(request))
        if retry_after is not None:
            raise HTTPException(
                status.HTTP_429_TOO_MANY_REQUESTS,
                "Too many requests. Please try again later.",
                headers={"Retry-After": str(retry_after)},
            )

    return _check
