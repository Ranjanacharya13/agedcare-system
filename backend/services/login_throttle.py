"""Failed-login lockout."""

import time
from collections import defaultdict

DEFAULT_MAX_ATTEMPTS = 5
DEFAULT_WINDOW_SECONDS = 900  # 15 minutes
DEFAULT_LOCKOUT_SECONDS = 900


class LoginThrottle:
    def __init__(
        self,
        max_attempts: int = DEFAULT_MAX_ATTEMPTS,
        window_seconds: int = DEFAULT_WINDOW_SECONDS,
        lockout_seconds: int = DEFAULT_LOCKOUT_SECONDS,
    ):
        self._max_attempts = max_attempts
        self._window = window_seconds
        self._lockout = lockout_seconds
        self._failures: dict[str, list[float]] = defaultdict(list)

    def _prune(self, key: str, now: float) -> list[float]:
        recent = [t for t in self._failures[key] if now - t < self._window]
        self._failures[key] = recent
        return recent

    def blocked_for(self, key: str) -> int | None:
        """Seconds remaining in the lockout, or None if not locked out."""
        now = time.monotonic()
        recent = self._prune(key, now)
        if len(recent) < self._max_attempts:
            return None
        unblock_at = recent[-1] + self._lockout
        remaining = int(unblock_at - now)
        return remaining if remaining > 0 else None

    def record_failure(self, key: str) -> None:
        now = time.monotonic()
        self._prune(key, now)
        self._failures[key].append(now)

    def clear(self, key: str) -> None:
        self._failures.pop(key, None)


#: Shared across requests so counts accumulate; created once at import.
login_throttle = LoginThrottle()
