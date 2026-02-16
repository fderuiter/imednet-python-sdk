"""
HTTP request execution with retries and monitoring.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Awaitable, Callable, Coroutine, Optional, TYPE_CHECKING, cast

import httpx
from tenacity import (
    AsyncRetrying,
    RetryCallState,
    RetryError,
    Retrying,
    stop_after_attempt,
    wait_exponential,
)

from imednet.core.retry import DefaultRetryPolicy, RetryPolicy, RetryState
from imednet.core.http.handlers import handle_response
from imednet.core.http.monitor import RequestMonitor

if TYPE_CHECKING:
    from opentelemetry.trace import Tracer
else:
    Tracer = Any


@dataclass
class RequestExecutor:
    """Execute HTTP requests with retry and error handling."""

    send: Callable[..., Awaitable[httpx.Response] | httpx.Response]
    is_async: bool
    retries: int
    backoff_factor: float
    tracer: Optional[Tracer] = None
    retry_policy: RetryPolicy | None = None

    def __post_init__(self) -> None:
        if self.retry_policy is None:
            self.retry_policy = DefaultRetryPolicy()

    def _get_retry_predicate(self, method: str) -> Callable[[RetryCallState], bool]:
        """Return a retry predicate that includes the HTTP method in state."""
        policy = self.retry_policy or DefaultRetryPolicy()

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

    def __call__(
        self, method: str, url: str, **kwargs: Any
    ) -> Coroutine[Any, Any, httpx.Response] | httpx.Response:
        if self.is_async:
            return self._async_execute(method, url, **kwargs)
        return self._sync_execute(method, url, **kwargs)

    def _execute_with_retry_sync(
        self,
        send_fn: Callable[[], httpx.Response],
        method: str,
        url: str,
    ) -> httpx.Response:
        """Send a request with retry logic and tracing."""
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
                # monitor.on_retry_error raises RequestError

        return handle_response(response)

    async def _execute_with_retry_async(
        self,
        send_fn: Callable[[], Awaitable[httpx.Response]],
        method: str,
        url: str,
    ) -> httpx.Response:
        """Send a request with retry logic and tracing asynchronously."""
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

    def _sync_execute(self, method: str, url: str, **kwargs: Any) -> httpx.Response:
        def send_fn() -> httpx.Response:
            return cast(httpx.Response, self.send(method, url, **kwargs))

        return cast(
            httpx.Response,
            self._execute_with_retry_sync(send_fn, method, url),
        )

    async def _async_execute(self, method: str, url: str, **kwargs: Any) -> httpx.Response:
        async def send_fn() -> httpx.Response:
            return await cast(Awaitable[httpx.Response], self.send(method, url, **kwargs))

        return await cast(
            Awaitable[httpx.Response],
            self._execute_with_retry_async(send_fn, method, url),
        )
