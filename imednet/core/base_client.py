# Base HTTP client for iMednet SDK

from __future__ import annotations

import logging
from typing import Any, Optional, Union

try:
    from opentelemetry import trace
    from opentelemetry.trace import Tracer
except Exception:  # pragma: no cover - optional dependency
    trace = None
    Tracer = None
import httpx

from imednet.config import load_config
from imednet.utils import sanitize_base_url
from imednet.utils.json_logging import configure_json_logging

logger = logging.getLogger(__name__)


class BaseClient:
    """Common initialization logic for HTTP clients."""

    DEFAULT_BASE_URL = "https://edc.prod.imednetapi.com"

    def __init__(
        self,
        api_key: Optional[str] = None,
        security_key: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: Union[float, httpx.Timeout] = 30.0,
        retries: int = 3,
        backoff_factor: float = 1.0,
        log_level: Union[int, str] = logging.INFO,
        tracer: Optional[Tracer] = None,
    ) -> None:
        config = load_config(api_key=api_key, security_key=security_key, base_url=base_url)

        self.base_url = sanitize_base_url(config.base_url or self.DEFAULT_BASE_URL)

        self.timeout = timeout if isinstance(timeout, httpx.Timeout) else httpx.Timeout(timeout)
        self.retries = retries
        self.backoff_factor = backoff_factor

        level = logging.getLevelName(log_level.upper()) if isinstance(log_level, str) else log_level
        configure_json_logging(level)
        logger.setLevel(level)

        self._client = self._create_client(config.api_key, config.security_key)

        if tracer is not None:
            self._tracer = tracer
        elif trace is not None:
            self._tracer = trace.get_tracer(__name__)
        else:
            self._tracer = None

    def _create_client(self, api_key: str, security_key: str) -> Any:
        raise NotImplementedError
