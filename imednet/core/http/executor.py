"""
HTTP request execution with retries and monitoring.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, Awaitable, Callable, Optional

import httpx
from tenacity import (
    AsyncRetrying,
    RetryCallState,
    RetryError,
    Retrying,
    stop_after_attempt,
    wait_exponential,
)

from imednet.core.http.handlers import handle_response
from imednet.core.http.monitor import RequestMonitor
from imednet.core.retry import DefaultRetryPolicy, RetryPolicy, RetryState

if TYPE_CHECKING:
    from opentelemetry.trace import Tracer
else:
    Tracer = Any


class BaseRequestExecutor(ABC):
    """Abstract base for request executors."""

    def __init__(
        self,
        send: Any,
        retries: int,
        backoff_factor: float,
        tracer: Optional[Tracer] = None,
        retry_policy: RetryPolicy | None = None,
    ) -> None:
        self.send = send
        self.retries = retries
        self.backoff_factor = backoff_factor
        self.tracer = tracer
        self.retry_policy = retry_policy or DefaultRetryPolicy()

    def _get_retry_predicate(self, method: str) -> Callable[[RetryCallState], bool]:
        """Return a retry predicate that includes the HTTP method in state."""
        policy = self.retry_policy

        def should_retry(retry_state: RetryCallState) -> bool:
            state = RetryState(
                attempt_number=retry_state.attempt_number,
                exception=(
                    retry_state.outcome.exception()
                    if retry_state.outcome and retry_state.outcome.failed
                    else None
                ),
                result=(
                    retry_state.outcome.result()
                    if retry_state.outcome and not retry_state.outcome.failed
                    else None
                ),
                method=method,
            )
            return policy.should_retry(state)

        return should_retry

    @abstractmethod
    def __call__(self, method: str, url: str, **kwargs: Any) -> Any:
        """Execute the request."""


class SyncRequestExecutor(BaseRequestExecutor):
    """Execute synchronous HTTP requests with retry and error handling."""

    def __init__(
        self,
        send: Callable[..., httpx.Response],
        retries: int,
        backoff_factor: float,
        tracer: Optional[Tracer] = None,
        retry_policy: RetryPolicy | None = None,
    ) -> None:
        super().__init__(send, retries, backoff_factor, tracer, retry_policy)
        # self.send is set in super

    def __call__(self, method: str, url: str, **kwargs: Any) -> httpx.Response:
        def send_fn() -> httpx.Response:
            return self.send(method, url, **kwargs)

        retryer = Retrying(
            stop=stop_after_attempt(self.retries),
            wait=wait_exponential(multiplier=self.backoff_factor),
            retry=self._get_retry_predicate(method),
            reraise=False,
        )

        with RequestMonitor(self.tracer, method, url) as monitor:
            try:
                response: httpx.Response = retryer(send_fn)
                monitor.on_success(response)
            except RetryError as e:
                monitor.on_retry_error(e)

        return handle_response(response)


class AsyncRequestExecutor(BaseRequestExecutor):
    """Execute asynchronous HTTP requests with retry and error handling."""

    def __init__(
        self,
        send: Callable[..., Awaitable[httpx.Response]],
        retries: int,
        backoff_factor: float,
        tracer: Optional[Tracer] = None,
        retry_policy: RetryPolicy | None = None,
    ) -> None:
        super().__init__(send, retries, backoff_factor, tracer, retry_policy)
        # self.send is set in super

    async def __call__(self, method: str, url: str, **kwargs: Any) -> httpx.Response:
        async def send_fn() -> httpx.Response:
            return await self.send(method, url, **kwargs)

        retryer = AsyncRetrying(
            stop=stop_after_attempt(self.retries),
            wait=wait_exponential(multiplier=self.backoff_factor),
            retry=self._get_retry_predicate(method),
            reraise=False,
        )

        async with RequestMonitor(self.tracer, method, url) as monitor:
            try:
                response: httpx.Response = await retryer(send_fn)
                monitor.on_success(response)
            except RetryError as e:
                monitor.on_retry_error(e)

        return handle_response(response)
