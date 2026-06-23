"""Retry logic and policies for iMedNet API requests."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional, Protocol, runtime_checkable

import httpx

#: HTTP methods that are safe to retry automatically. Mutating methods such as
#: POST and PATCH are intentionally excluded because a server may have already
#: processed the request before the connection dropped, and retrying would risk
#: creating duplicate records or corrupting state.
IDEMPOTENT_METHODS: frozenset[str] = frozenset({"GET", "PUT", "DELETE", "HEAD", "OPTIONS"})


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
    """Retry policy with idempotency-aware retry logic.

    - **Network errors** (``httpx.RequestError``) and **server errors** (HTTP
      500-599) are only retried for idempotent HTTP methods:
      ``GET``, ``PUT``, ``DELETE``, ``HEAD``, and ``OPTIONS``.
    - **Rate-limit responses** (HTTP 429) are retried for *all* methods because
      the server rejected the request before processing the payload, so there is
      no risk of duplicate side-effects.
    - Requests with an unknown or missing method are treated as non-idempotent
      (fail-safe default): they are *not* retried on network errors or 5xx
      responses.

    **Overriding this behaviour**

    If you need retries on a ``POST`` endpoint that is internally deduplicated
    (e.g. the server uses an idempotency key), subclass :class:`RetryPolicy`
    and pass an instance to the client::

        from imednet.core.retry import RetryPolicy, RetryState, IDEMPOTENT_METHODS
        import httpx

        class IdempotentPostPolicy(RetryPolicy):
            def should_retry(self, state: RetryState) -> bool:
                method = (state.method or "").upper()
                if state.exception:
                    return isinstance(state.exception, httpx.RequestError)
                response = state.result
                if isinstance(response, httpx.Response):
                    return (
                        response.status_code == 429
                        or 500 <= response.status_code < 600
                    )
                return False

        sdk = ImednetSDK(..., retry_policy=IdempotentPostPolicy())
    """

    def should_retry(self, state: RetryState) -> bool:
        """Return True if the request should be retried based on the state."""
        method = (state.method or "").upper()
        is_idempotent = method in IDEMPOTENT_METHODS

        if state.exception:
            return is_idempotent and isinstance(state.exception, httpx.RequestError)

        response = state.result
        if isinstance(response, httpx.Response):
            if response.status_code == 429:
                return True
            return is_idempotent and 500 <= response.status_code < 600

        return False
