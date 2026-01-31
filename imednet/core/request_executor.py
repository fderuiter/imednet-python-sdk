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

    def _should_retry(self, retry_state: RetryCallState) -> bool:
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
        )
        policy = self.retry_policy or DefaultRetryPolicy()
        return policy.should_retry(state)

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

    def _get_span_cm(self, method: str, url: str):
        if self.tracer:
            return self.tracer.start_as_current_span(
                "http_request", attributes={"endpoint": url, "method": method}
            )
        return nullcontext()

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
            retry=self._should_retry,
            reraise=True,
        )

        with self._get_span_cm(method, url) as span:
            try:
                start = time.monotonic()
                response: httpx.Response = retryer(send_fn)
                latency = time.monotonic() - start
                logger.info(
                    "http_request",
                    extra={
                        "method": method,
                        "url": url,
                        "status_code": response.status_code,
                        "latency": latency,
                    },
                )
            except RetryError as e:
                logger.error("Request failed after retries: %s", e)
                raise RequestError("Network request failed after retries")

            if span is not None:
                span.set_attribute("status_code", response.status_code)

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
            retry=self._should_retry,
            reraise=True,
        )

        async with self._get_span_cm(method, url) as span:
            try:
                start = time.monotonic()
                response: httpx.Response = await retryer(send_fn)
                latency = time.monotonic() - start
                logger.info(
                    "http_request",
                    extra={
                        "method": method,
                        "url": url,
                        "status_code": response.status_code,
                        "latency": latency,
                    },
                )
            except RetryError as e:
                logger.error("Request failed after retries: %s", e)
                raise RequestError("Network request failed after retries")

            if span is not None:
                span.set_attribute("status_code", response.status_code)

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
