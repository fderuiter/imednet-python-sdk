"""
HTTP request execution with retries and monitoring.
"""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from contextlib import contextmanager
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from typing import TYPE_CHECKING, Any, Awaitable, Callable, Iterator, Optional

import httpx
from tenacity import (
    AsyncRetrying,
    RetryCallState,
    RetryError,
    Retrying,
    stop_after_attempt,
    wait_random_exponential,
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
        self._jitter_wait = wait_random_exponential(multiplier=self.backoff_factor)

    @staticmethod
    @contextmanager
    def _suppress_httpx_request_logging() -> Iterator[None]:
        logger_names = ("httpx", "httpcore", *list(logging.root.manager.loggerDict.keys()))
        loggers: dict[str, logging.Logger] = {}
        for name in logger_names:
            if name in ("httpx", "httpcore") or name.startswith(("httpx.", "httpcore.")):
                loggers[name] = logging.getLogger(name)

        logger_states = {logger: logger.level for logger in loggers.values()}
        for logger in logger_states:
            logger.setLevel(logging.WARNING)
        try:
            yield
        finally:
            for logger, original_level in logger_states.items():
                logger.setLevel(original_level)

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

    def _process_result(
        self, response: Optional[httpx.Response], monitor: RequestMonitor
    ) -> httpx.Response:
        """Process successful response or raise error if None."""
        if response is not None:
            monitor.on_success(response)
            return handle_response(response)
        raise RuntimeError("Request failed without response or exception")

    def _process_retry_error(self, e: RetryError, monitor: RequestMonitor) -> httpx.Response:
        """Handle RetryError, extracting successful result if present, else escalate."""
        if e.last_attempt and not e.last_attempt.failed:
            response: httpx.Response = e.last_attempt.result()
            monitor.on_success(response)
            return handle_response(response)
        monitor.on_retry_error(e)
        raise RuntimeError("Request failed without response or exception")  # Unreachable

    @staticmethod
    def _parse_retry_after_seconds(response: httpx.Response) -> Optional[float]:
        value = response.headers.get("Retry-After")
        if not value:
            return None

        try:
            delay = float(value)
            return max(delay, 0.0)
        except ValueError:
            pass

        try:
            retry_time = parsedate_to_datetime(value)
            if retry_time.tzinfo is None:
                retry_time = retry_time.replace(tzinfo=timezone.utc)
            delay = (retry_time - datetime.now(timezone.utc)).total_seconds()
            return max(delay, 0.0)
        except (TypeError, ValueError, OverflowError):
            return None

    def _wait_strategy(self, retry_state: RetryCallState) -> float:
        if retry_state.outcome and not retry_state.outcome.failed:
            result = retry_state.outcome.result()
            if isinstance(result, httpx.Response):
                retry_after_seconds = self._parse_retry_after_seconds(result)
                if retry_after_seconds is not None:
                    return retry_after_seconds
        return float(self._jitter_wait(retry_state))

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
            with self._suppress_httpx_request_logging():
                return self.send(method, url, **kwargs)

        retryer = Retrying(
            stop=stop_after_attempt(self.retries),
            wait=self._wait_strategy,
            retry=self._get_retry_predicate(method),
            reraise=False,
        )

        with RequestMonitor(self.tracer, method, url) as monitor:
            try:
                response: Optional[httpx.Response] = retryer(send_fn)
                return self._process_result(response, monitor)
            except RetryError as e:
                return self._process_retry_error(e, monitor)


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
            with self._suppress_httpx_request_logging():
                return await self.send(method, url, **kwargs)

        retryer = AsyncRetrying(
            stop=stop_after_attempt(self.retries),
            wait=self._wait_strategy,
            retry=self._get_retry_predicate(method),
            reraise=False,
        )

        async with RequestMonitor(self.tracer, method, url) as monitor:
            try:
                response: Optional[httpx.Response] = await retryer(send_fn)
                return self._process_result(response, monitor)
            except RetryError as e:
                return self._process_retry_error(e, monitor)
