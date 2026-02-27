from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional, Protocol, runtime_checkable

import httpx


@dataclass
class RetryState:
    """State information passed to :class:`RetryPolicy`."""

    attempt_number: int
    exception: Optional[BaseException] = None
    result: Optional[Any] = None
    method: Optional[str] = None


@runtime_checkable
class RetryPolicy(Protocol):
    """Interface to determine whether a request should be retried."""

    def should_retry(self, state: RetryState) -> bool:
        """Return ``True`` to retry the request for the given state."""


class DefaultRetryPolicy:
    """Retry on network errors, rate limits (429), and server errors (500-599)."""

    def should_retry(self, state: RetryState) -> bool:
        if state.exception:
            return isinstance(state.exception, httpx.RequestError)

        response = state.result
        if isinstance(response, httpx.Response):
            return response.status_code == 429 or 500 <= response.status_code < 600

        return False
