from __future__ import annotations

import logging
import time
from contextlib import nullcontext
from dataclasses import dataclass
from typing import Any, Awaitable, Callable, Coroutine, Optional, cast

import httpx
from tenacity import (
    AsyncRetrying,
    RetryCallState,
    RetryError,
    Retrying,
    stop_after_attempt,
    wait_exponential,
)

from ..utils.url import redact_url_query
from .base_client import Tracer
from .exceptions import (
    ApiError,
    BadRequestError,
    ConflictError,
    ForbiddenError,
    NotFoundError,
    RateLimitError,
    RequestError,
    ServerError,
    UnauthorizedError,
)
from .retry import DefaultRetryPolicy, RetryPolicy, RetryState

logger = logging.getLogger(__name__)

STATUS_TO_ERROR: dict[int, type[ApiError]] = {
    400: BadRequestError,
    401: UnauthorizedError,
    403: ForbiddenError,
    404: NotFoundError,
    409: ConflictError,
    429: RateLimitError,
}


class RequestMonitor:
    """Helper to handle request monitoring (tracing, timing, logging)."""

    def __init__(self, tracer: Optional[Tracer], method: str, url: str) -> None:
        self.tracer = tracer
        self.method = method
        self.safe_url = redact_url_query(url)
        self.start_time: float = 0.0
        self.span: Any = None
        self._cm: Any = None

    def _create_cm(self) -> Any:
        if self.tracer:
            return self.tracer.start_as_current_span(
                "http_request",
                attributes={"endpoint": self.safe_url, "method": self.method},
            )
        return nullcontext()

    def __enter__(self) -> RequestMonitor:
        self._cm = self._create_cm()
        self.span = self._cm.__enter__()
        self.start_time = time.monotonic()
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        if self._cm:
            self._cm.__exit__(exc_type, exc_val, exc_tb)

    async def __aenter__(self) -> RequestMonitor:
        self._cm = self._create_cm()
        # Handle async context managers if the tracer supports them
        if hasattr(self._cm, "__aenter__"):
            self.span = await self._cm.__aenter__()
        else:
            self.span = self._cm.__enter__()
        self.start_time = time.monotonic()
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        if self._cm:
            if hasattr(self._cm, "__aexit__"):
                await self._cm.__aexit__(exc_type, exc_val, exc_tb)
            else:
                self._cm.__exit__(exc_type, exc_val, exc_tb)

    def on_success(self, response: httpx.Response) -> None:
        latency = time.monotonic() - self.start_time
        logger.info(
            "http_request",
            extra={
                "method": self.method,
                "url": self.safe_url,
                "status_code": response.status_code,
                "latency": latency,
            },
        )
        if self.span:
            self.span.set_attribute("status_code", response.status_code)

    def on_retry_error(self, e: RetryError) -> None:
        logger.error("Request failed after retries: %s", e)
        raise RequestError("Network request failed after retries") from e


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

    def _handle_response(self, response: httpx.Response) -> httpx.Response:
        """Return the response or raise an appropriate ``ApiError``."""
        if response.is_error:
            status = response.status_code
            try:
                body = response.json()
            except Exception:
                body = response.text
            exc_cls = STATUS_TO_ERROR.get(status)
            if exc_cls:
                raise exc_cls(body)
            if 500 <= status < 600:
                raise ServerError(body)
            raise ApiError(body)
        return response

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
            reraise=True,
        )

        with RequestMonitor(self.tracer, method, url) as monitor:
            try:
                response = retryer(send_fn)
                monitor.on_success(response)
            except RetryError as e:
                monitor.on_retry_error(e)

        return self._handle_response(response)

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
            reraise=True,
        )

        async with RequestMonitor(self.tracer, method, url) as monitor:
            try:
                response = await retryer(send_fn)
                monitor.on_success(response)
            except RetryError as e:
                monitor.on_retry_error(e)

        return self._handle_response(response)

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
