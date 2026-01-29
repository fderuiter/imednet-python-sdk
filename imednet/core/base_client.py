# Base HTTP client for iMednet SDK

from __future__ import annotations

import logging
import os
from typing import Any, Optional, Union

try:
    from opentelemetry import trace
    from opentelemetry.trace import Tracer
except Exception:  # pragma: no cover - optional dependency
    trace = None
    Tracer = None
import httpx

from imednet.auth.api_key import ApiKeyAuth
from imednet.auth.strategy import AuthStrategy
from imednet.config import load_config
from imednet.constants import (
    DEFAULT_BACKOFF_FACTOR,
    DEFAULT_BASE_URL,
    DEFAULT_RETRIES,
    DEFAULT_TIMEOUT,
)
from imednet.utils import sanitize_base_url

logger = logging.getLogger(__name__)


class BaseClient:
    """Common initialization logic for HTTP clients."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        security_key: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: Union[float, httpx.Timeout] = DEFAULT_TIMEOUT,
        retries: int = DEFAULT_RETRIES,
        backoff_factor: float = DEFAULT_BACKOFF_FACTOR,
        tracer: Optional[Tracer] = None,
        auth: Optional[AuthStrategy] = None,
    ) -> None:
        self.auth: AuthStrategy

        if auth:
            self.auth = auth
            base_url = base_url if base_url is not None else os.getenv("IMEDNET_BASE_URL")
            self.base_url = sanitize_base_url(base_url or DEFAULT_BASE_URL)
        else:
            config = load_config(api_key=api_key, security_key=security_key, base_url=base_url)
            self.auth = ApiKeyAuth(config.api_key, config.security_key)
            self.base_url = sanitize_base_url(config.base_url or DEFAULT_BASE_URL)

        self.timeout = timeout if isinstance(timeout, httpx.Timeout) else httpx.Timeout(timeout)
        self.retries = retries
        self.backoff_factor = backoff_factor

        self._client = self._create_client()

        if tracer is not None:
            self._tracer = tracer
        elif trace is not None:
            self._tracer = trace.get_tracer(__name__)
        else:
            self._tracer = None

    def _create_client(self) -> Any:
        raise NotImplementedError
