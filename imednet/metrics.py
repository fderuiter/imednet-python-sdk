"""Optional Prometheus metrics for API calls."""

from __future__ import annotations

import logging

try:
    from prometheus_client import Counter, Summary, start_http_server
except Exception:  # pragma: no cover - optional dependency missing
    Counter = None  # type: ignore
    Summary = None  # type: ignore
    start_http_server = None  # type: ignore

logger = logging.getLogger(__name__)

metrics_enabled = False

if Counter and Summary:
    API_CALLS = Counter(
        "imednet_api_calls_total", "Total API calls made", ["method", "endpoint"]
    )
    API_LATENCY = Summary(
        "imednet_api_latency_seconds", "Latency of API requests", ["method", "endpoint"]
    )
else:  # pragma: no cover - metrics disabled when dependency missing
    API_CALLS = None
    API_LATENCY = None


def enable_metrics(port: int = 8000) -> None:
    """Enable Prometheus metrics by starting an HTTP server."""

    global metrics_enabled
    if not (Counter and Summary and start_http_server):
        raise ImportError("prometheus-client is not installed")
    if not metrics_enabled:
        logger.info("Starting metrics server on port %s", port)
        start_http_server(port)
        metrics_enabled = True
