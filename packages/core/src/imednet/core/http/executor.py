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

from imednet.core.http.circuit_breaker import CircuitBreakerError, get_global_circuit_breaker
from imednet.core.http.handlers import handle_response
from imednet.core.http.monitor import RequestMonitor
from imednet.core.retry import DefaultRetryPolicy, RetryPolicy, RetryState

_SUPPRESSED_LOG_LEVEL = logging.CRITICAL + 1

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
        loggers = {
            "httpx": logging.getLogger("httpx"),
            "httpcore": logging.getLogger("httpcore"),
        }
        logger_states = {name: logger.level for name, logger in loggers.items()}
        for logger in loggers.values():
            logger.setLevel(_SUPPRESSED_LOG_LEVEL)
        try:
            yield
        finally:
            for name, original_level in logger_states.items():
                loggers[name].setLevel(original_level)

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
            # We treat successful HTTP requests (even 4xx/5xx that don't raise here)
            # as a successful "connection" probe for the circuit breaker, but let's
            # check the response. If it's a 5xx, it might be an outage.
            # Usually, retries cover 5xx, but if we reach here and it's a 5xx that wasn't retried,
            # we should record failure? No, let's just record success if we got a response
            # that is not an exception, OR wait, an API outage usually manifests as connection errors
            # or 5xx. If handle_response raises, it will throw an exception below.

            # Record success before handle_response so if it raises, we know we got a response at least.
            # But 5xx server errors indicate failures. Let's record success only if status is < 500.
            if response.status_code < 500:
                get_global_circuit_breaker().record_success()
            else:
                get_global_circuit_breaker().record_failure()

            monitor.on_success(response)
            return handle_response(response)
        raise RuntimeError("Request failed without response or exception")

    def _process_retry_error(self, e: RetryError, monitor: RequestMonitor) -> httpx.Response:
        """Handle RetryError, extracting successful result if present, else escalate."""
        # A RetryError means we exhausted retries (which indicates consecutive failures)
        get_global_circuit_breaker().record_failure()

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
        get_global_circuit_breaker().check_request_allowed()

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
            except Exception as e:
                # If we get connection errors inside send_fn, they are wrapped by Tenacity RetryError?
                # Tenacity Catches exceptions, but if it doesn't retry, it raises.
                if isinstance(e, RetryError):
                    return self._process_retry_error(e, monitor)
                else:
                    get_global_circuit_breaker().record_failure()
                    raise


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
        get_global_circuit_breaker().check_request_allowed()

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
            except Exception as e:
                if isinstance(e, RetryError):
                    return self._process_retry_error(e, monitor)
                else:
                    get_global_circuit_breaker().record_failure()
                    raise
