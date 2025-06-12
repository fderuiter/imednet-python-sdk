# Optional Prometheus metrics helpers
from __future__ import annotations

from typing import TYPE_CHECKING, Any, Callable, Optional

if TYPE_CHECKING:  # pragma: no cover - used for type checking only
    from prometheus_client import Counter as PromCounter
    from prometheus_client import Histogram as PromHistogram

    start_http_server: Callable[[int], Any]
else:  # pragma: no cover - optional dependency at runtime
    try:
        from prometheus_client import (
            Counter as PromCounter,
        )
        from prometheus_client import (
            Histogram as PromHistogram,
        )
        from prometheus_client import (
            start_http_server as prom_start_http_server,
        )

        start_http_server: Callable[[int], Any] = prom_start_http_server
    except Exception:  # pragma: no cover - dependency missing
        PromCounter = None  # type: ignore
        PromHistogram = None  # type: ignore
        start_http_server = None

API_CALLS: Optional[PromCounter] = (
    PromCounter(
        "imednet_api_calls_total",
        "Total number of iMednet API calls",
        ["endpoint", "method", "status"],
    )
    if PromCounter is not None
    else None
)

API_LATENCY: Optional[PromHistogram] = (
    PromHistogram(
        "imednet_api_latency_seconds", "Latency of iMednet API calls", ["endpoint", "method"]
    )
    if PromHistogram is not None
    else None
)

_metrics_started = False


def enable_metrics(port: int = 8000) -> None:
    """Start the Prometheus metrics server if available."""
    global _metrics_started
    if start_http_server is None or _metrics_started:
        return
    start_http_server(port)
    _metrics_started = True
