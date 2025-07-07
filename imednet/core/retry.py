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


@runtime_checkable
class RetryPolicy(Protocol):
    """Interface to determine whether a request should be retried."""

    def should_retry(self, state: RetryState) -> bool:
        """Return ``True`` to retry the request for the given state."""


class DefaultRetryPolicy:
    """Retry only when a network :class:`httpx.RequestError` occurred."""

    def should_retry(self, state: RetryState) -> bool:  # pragma: no cover - trivial
        return isinstance(state.exception, httpx.RequestError)
