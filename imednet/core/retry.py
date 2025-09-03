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
    """A protocol for defining custom retry logic.

    This protocol allows users to implement their own retry strategies by providing
    a `should_retry` method.
    """

    def should_retry(self, state: RetryState) -> bool:
        """Determine whether a request should be retried.

        Args:
            state: The current state of the retry attempt.

        Returns:
            `True` to retry the request, `False` otherwise.
        """


class DefaultRetryPolicy:
    """The default retry policy.

    This policy retries requests only when a network error of type
    :class:`httpx.RequestError` occurs.
    """

    def should_retry(self, state: RetryState) -> bool:
        """Determine whether to retry based on the default policy.

        Args:
            state: The current state of the retry attempt.

        Returns:
            `True` if the exception is a `httpx.RequestError`, `False` otherwise.
        """
        return isinstance(state.exception, httpx.RequestError)
