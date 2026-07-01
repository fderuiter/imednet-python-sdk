"""Universal execution wrapper that applies exponential backoff retries and circuit breaking.

to any compliant operation.
"""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, Awaitable, Callable, Optional, TypeVar

from tenacity import RetryCallState, RetryError, wait_random_exponential

from imednet.core.operations.monitor import OperationMonitor

if TYPE_CHECKING:
    from opentelemetry.trace import Tracer
else:
    Tracer = Any

logger = logging.getLogger(__name__)

T = TypeVar("T")


class OperationRetryPolicy(ABC):
    """Base class for defining retry policies for operations."""

    @abstractmethod
    def should_retry(self, exception: Exception) -> bool:
        """Return True if the exception should trigger a retry."""
        pass


class DefaultOperationRetryPolicy(OperationRetryPolicy):
    """Default retry policy that retries on all exceptions."""

    def should_retry(self, exception: Exception) -> bool:
        """Return True if the exception should trigger a retry.

        Args:
            exception: The exception that occurred during execution.

        Returns:
            bool: True, as the default policy retries everything.
        """
        # Default fallback: retry on any exception?
        # Usually we only retry on specific ones, but for universal wrapper, we can allow everything or leave it configurable
        return True


class UniversalExecutor:
    """Execute arbitrary operations with retry, circuit breaking, and telemetry."""

    def __init__(
        self,
        retries: int,
        backoff_factor: float,
        tracer: Optional[Tracer] = None,
        retry_policy: Optional[OperationRetryPolicy] = None,
        operation_name: str = "operation",
        wait_strategy: Optional[Callable[[RetryCallState], float]] = None,
        retry_predicate: Optional[Callable[[RetryCallState], bool]] = None,
        **attributes: Any,
    ) -> None:
        """Initialize the executor.

        Args:
            retries: Maximum number of retry attempts.
            backoff_factor: Factor for exponential backoff wait calculation.
            tracer: Optional OpenTelemetry tracer for monitoring.
            retry_policy: Policy defining which exceptions should be retried.
            operation_name: Name of the operation (used in logs and spans).
            wait_strategy: Optional custom wait strategy function.
            retry_predicate: Optional custom retry predicate function.
            **attributes: Additional attributes to attach to logs and spans.
        """
        self.retries = retries
        self.backoff_factor = backoff_factor
        self.tracer = tracer
        self.retry_policy = retry_policy or DefaultOperationRetryPolicy()
        self.operation_name = operation_name
        self.attributes = attributes
        self._jitter_wait = wait_random_exponential(multiplier=self.backoff_factor)
        self.wait_strategy = wait_strategy or (lambda rs: float(self._jitter_wait(rs)))
        self.retry_predicate = retry_predicate or self._should_retry_wrapper

    def _should_retry_wrapper(self, retry_state: RetryCallState) -> bool:
        """Internal wrapper to adapt Tenacity's retry state to the retry policy.

        Args:
            retry_state: Tenacity's retry state.

        Returns:
            bool: True if the operation should be retried.
        """
        if retry_state.outcome and retry_state.outcome.failed:
            exc = retry_state.outcome.exception()
            if isinstance(exc, Exception):
                return self.retry_policy.should_retry(exc)
        return False

    def execute(self, func: Callable[[], T]) -> T:
        """Synchronous execution."""
        from imednet.core.policy_runner import PolicyRunner

        runner = PolicyRunner(
            retries=self.retries,
            backoff_factor=self.backoff_factor,
            wait_strategy=self.wait_strategy,
            retry_predicate=self.retry_predicate,
        )

        with OperationMonitor(self.tracer, self.operation_name, **self.attributes) as monitor:
            try:
                result: Any = runner.execute(func)
                monitor.on_success()
                return result
            except RetryError as e:
                cause = e.last_attempt.exception() if e.last_attempt else e
                if isinstance(cause, Exception):
                    try:
                        monitor.on_retry_error(cause, self.retries)
                    except Exception as _exc:
                        if _exc is not cause:
                            raise
                if cause is not None and cause is not e:
                    raise cause
                raise
            except Exception as e:
                monitor.on_failure(e)
                raise

    async def execute_async(self, func: Callable[[], Awaitable[T]]) -> T:
        """Asynchronous execution."""
        from imednet.core.policy_runner import PolicyRunner

        runner = PolicyRunner(
            retries=self.retries,
            backoff_factor=self.backoff_factor,
            wait_strategy=self.wait_strategy,
            retry_predicate=self.retry_predicate,
        )

        async with OperationMonitor(self.tracer, self.operation_name, **self.attributes) as monitor:
            try:

                async def _async_wrapper() -> T:
                    """Wrapper to await the function.

                    Returns:
                        T: Result of the operation.
                    """
                    return await func()

                result: Any = await runner.execute_async(_async_wrapper)
                monitor.on_success()
                return result
            except RetryError as e:
                cause = e.last_attempt.exception() if e.last_attempt else e
                if isinstance(cause, Exception):
                    try:
                        monitor.on_retry_error(cause, self.retries)
                    except Exception as _exc:
                        if _exc is not cause:
                            raise
                if cause is not None and cause is not e:
                    raise cause
                raise
            except Exception as e:
                monitor.on_failure(e)
                raise
