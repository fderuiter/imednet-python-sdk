"""
Request monitoring and tracing.
"""

from __future__ import annotations

import logging
import time
from contextlib import nullcontext
from typing import TYPE_CHECKING, Any, NoReturn, Optional

import httpx
from tenacity import RetryError

from imednet.core.exceptions import RequestError
from imednet.utils.url import redact_url_query

if TYPE_CHECKING:
    from opentelemetry.trace import Tracer  # pragma: no cover
else:
    Tracer = Any

logger = logging.getLogger(__name__)


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

    def __enter__(self) -> "RequestMonitor":
        self._cm = self._create_cm()
        self.span = self._cm.__enter__()
        self.start_time = time.monotonic()
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        if self._cm:
            self._cm.__exit__(exc_type, exc_val, exc_tb)

    async def __aenter__(self) -> "RequestMonitor":
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

    def on_retry_error(self, e: RetryError) -> NoReturn:
        logger.error("Request failed after retries: %s", e)
        cause = e.last_attempt.exception() if e.last_attempt else e
        raise RequestError("Network request failed after retries") from cause
