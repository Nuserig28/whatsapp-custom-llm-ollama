import time
from collections import deque
from typing import Deque, Dict


class SlidingWindowRateLimiter:
    """
    In-memory sliding window rate limiter.

    Notes:
    - Per-process only (uvicorn workers > 1 -> each worker has its own limiter).
    - Resets on restart (fine for this project).
    """

    def __init__(self) -> None:
        self._events: Dict[str, Deque[float]] = {}

    def allow(self, key: str, limit: int, window_seconds: int) -> bool:
        now = time.time()

        q = self._events.get(key)
        if q is None:
            q = deque()
            self._events[key] = q

        cutoff = now - window_seconds
        while q and q[0] <= cutoff:
            q.popleft()

        if len(q) >= limit:
            return False

        q.append(now)
        return True
