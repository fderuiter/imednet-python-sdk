"""Unified policy runner for circuit breaking and retries."""

import logging
from typing import Any, Awaitable, Callable, Optional, TypeVar

from tenacity import (
    AsyncRetrying,
    RetryCallState,
    Retrying,
    stop_after_attempt,
    wait_random_exponential,
)

from imednet.core.operations.circuit_breaker import get_global_circuit_breaker

T = TypeVar("T")
logger = logging.getLogger(__name__)


class PolicyRunner:
    """Unified policy runner for executing operations with retries and circuit breaking."""

    def __init__(
        self,
        retries: int,
        backoff_factor: float,
        wait_strategy: Optional[Callable[[RetryCallState], float]] = None,
        retry_predicate: Optional[Callable[[RetryCallState], bool]] = None,
        result_evaluator: Optional[Callable[[Any], bool]] = None,
    ) -> None:
        """Initialize the policy runner.

        Args:
            retries: Maximum number of retries (attempted after the initial call).
            backoff_factor: Exponential backoff factor.
            wait_strategy: Optional custom wait strategy.
            retry_predicate: Optional custom retry condition.
            result_evaluator: Optional callback to determine if a result is a success.
        """
        self.retries = retries
        self.backoff_factor = backoff_factor
        self._jitter_wait = wait_random_exponential(multiplier=self.backoff_factor)
        self.wait_strategy = wait_strategy or (lambda rs: float(self._jitter_wait(rs)))
        self.retry_predicate = retry_predicate
        self.result_evaluator = result_evaluator

    def __enter__(self) -> "PolicyRunner":
        """Enter the context manager and check circuit breaker."""
        get_global_circuit_breaker().check_request_allowed()
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Exit the context manager and record failure if exception occurred."""
        if exc_type is not None:
            get_global_circuit_breaker().record_failure()

    async def __aenter__(self) -> "PolicyRunner":
        """Enter the async context manager and check circuit breaker."""
        get_global_circuit_breaker().check_request_allowed()
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Exit the async context manager and record failure if exception occurred."""
        if exc_type is not None:
            get_global_circuit_breaker().record_failure()

    def execute(self, func: Callable[[], T]) -> T:
        """Execute a synchronous function with policy enforcement.

        Args:
            func: The function to execute.

        Returns:
            T: The result of the function.
        """
        with self:
            retryer = Retrying(
                stop=stop_after_attempt(self.retries + 1),
                wait=self.wait_strategy,
                retry=self.retry_predicate,
                reraise=False,
            )
            result = retryer(func)

            if self.result_evaluator and not self.result_evaluator(result):
                get_global_circuit_breaker().record_failure()
            else:
                get_global_circuit_breaker().record_success()

            return result

    async def execute_async(self, func: Callable[[], Awaitable[T]]) -> T:
        """Execute an asynchronous function with policy enforcement.

        Args:
            func: The async function to execute.

        Returns:
            T: The result of the function.
        """
        async with self:
            retryer = AsyncRetrying(
                stop=stop_after_attempt(self.retries + 1),
                wait=self.wait_strategy,
                retry=self.retry_predicate,
                reraise=False,
            )
            result = await retryer(func)

            if self.result_evaluator and not self.result_evaluator(result):
                get_global_circuit_breaker().record_failure()
            else:
                get_global_circuit_breaker().record_success()

            return result
