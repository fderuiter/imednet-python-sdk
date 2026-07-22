# pylint: disable=duplicate-code
"""Monitoring utilities for iMednet operations, supporting tracing and logging."""

from __future__ import annotations

import logging
import time
from contextlib import nullcontext
from typing import TYPE_CHECKING, Any, NoReturn

if TYPE_CHECKING:
    from opentelemetry.trace import Tracer
else:
    Tracer = Any

logger = logging.getLogger(__name__)


class OperationMonitor:
    """Helper to handle generic operation monitoring (tracing, timing, logging)."""

    def __init__(self, tracer: Tracer | None, operation_name: str, **attributes: Any) -> None:
        """Initialize the operation monitor.

        Args:
            tracer: OpenTelemetry tracer to use for creating spans.
            operation_name: Name of the operation being monitored.
            **attributes: Key-value pairs to attach to the operation span/log.
        """
        self.tracer = tracer
        self.operation_name = operation_name
        self.attributes = attributes
        self.start_time: float = 0.0
        self.span: Any = None
        self._cm: Any = None

    def _create_cm(self) -> Any:
        """Create a context manager for the operation span.

        Returns:
            Any: A context manager (either a span or a null context).
        """
        if self.tracer:
            return self.tracer.start_as_current_span(
                self.operation_name,
                attributes=self.attributes,
            )
        return nullcontext()

    def __enter__(self) -> OperationMonitor:
        """Enter the synchronous monitoring context.

        Returns:
            OperationMonitor: The monitor instance.
        """
        self._cm = self._create_cm()
        self.span = self._cm.__enter__()
        self.start_time = time.monotonic()
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Exit the synchronous monitoring context.

        Args:
            exc_type: Exception type if an error occurred.
            exc_val: Exception value if an error occurred.
            exc_tb: Exception traceback if an error occurred.
        """
        if self._cm:
            self._cm.__exit__(exc_type, exc_val, exc_tb)

    async def __aenter__(self) -> OperationMonitor:
        """Enter the asynchronous monitoring context.

        Returns:
            OperationMonitor: The monitor instance.
        """
        self._cm = self._create_cm()
        # Handle async context managers if the tracer supports them
        if hasattr(self._cm, "__aenter__"):
            self.span = await self._cm.__aenter__()
        else:
            self.span = self._cm.__enter__()
        self.start_time = time.monotonic()
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Exit the asynchronous monitoring context.

        Args:
            exc_type: Exception type if an error occurred.
            exc_val: Exception value if an error occurred.
            exc_tb: Exception traceback if an error occurred.
        """
        if self._cm:
            if hasattr(self._cm, "__aexit__"):
                await self._cm.__aexit__(exc_type, exc_val, exc_tb)
            else:
                self._cm.__exit__(exc_type, exc_val, exc_tb)

    def on_success(self, **extra_attributes: Any) -> None:
        """Record a successful operation completion.

        Args:
            **extra_attributes: Additional attributes to log or attach to the span.
        """
        latency = time.monotonic() - self.start_time
        logger.info(
            f"{self.operation_name} succeeded",
            extra={**self.attributes, **extra_attributes, "latency": latency},
        )
        if self.span:
            for k, v in extra_attributes.items():
                self.span.set_attribute(k, v)
            self.span.set_attribute("status", "success")

    def on_retry_error(self, cause: Exception, retries: int) -> NoReturn:
        """Record a failure after all retries are exhausted.

        Args:
            cause: The final exception that caused the failure.
            retries: Number of retries attempted.

        Raises:
            Exception: Re-raises the cause exception.
        """
        logger.error(
            f"{self.operation_name} failed after retries",
            extra={**self.attributes, "retries": retries},
        )
        if self.span:
            self.span.set_attribute("status", "failed")
            self.span.set_attribute("retries", retries)
        raise cause

    def on_failure(self, cause: Exception) -> None:
        """Record an operation failure.

        Args:
            cause: The exception that caused the failure.
        """
        if self.span:
            self.span.set_attribute("status", "failed")
