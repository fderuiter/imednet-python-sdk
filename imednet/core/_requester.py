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
    should_retry: Callable[[RetryCallState], bool] | None = None

    def _default_should_retry(self, retry_state: RetryCallState) -> bool:
        if retry_state.outcome is None:
            return False
        exc = retry_state.outcome.exception()
        return isinstance(exc, httpx.RequestError)

    def __call__(
        self, method: str, url: str, **kwargs: Any
    ) -> Coroutine[Any, Any, httpx.Response] | httpx.Response:
        if self.is_async:
            return self._async_execute(method, url, **kwargs)
        return self._sync_execute(method, url, **kwargs)

    def _handle_response(self, response: httpx.Response) -> httpx.Response:
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

    def _sync_execute(self, method: str, url: str, **kwargs: Any) -> httpx.Response:
        retryer = Retrying(
            stop=stop_after_attempt(self.retries),
            wait=wait_exponential(multiplier=self.backoff_factor),
            retry=self.should_retry or self._default_should_retry,
            reraise=True,
        )

        with self._get_span_cm(method, url) as span:
            try:
                start = time.monotonic()
                response = retryer(lambda: cast(httpx.Response, self.send(method, url, **kwargs)))
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

    async def _async_execute(self, method: str, url: str, **kwargs: Any) -> httpx.Response:
        retryer = AsyncRetrying(
            stop=stop_after_attempt(self.retries),
            wait=wait_exponential(multiplier=self.backoff_factor),
            retry=self.should_retry or self._default_should_retry,
            reraise=True,
        )

        async with self._get_span_cm(method, url) as span:
            try:
                start = time.monotonic()
                async for attempt in retryer:
                    with attempt:
                        response = await cast(
                            Awaitable[httpx.Response],
                            self.send(method, url, **kwargs),
                        )
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
