# Base HTTP client for iMednet SDK

"""TODO: Add docstring."""
from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any, Optional, Union

if TYPE_CHECKING:
    from opentelemetry.trace import Tracer
else:  # pragma: no cover - typing fallback for optional dependency
    Tracer = Any

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

trace: Any = None
try:
    from opentelemetry import trace as _trace

    trace = _trace
except Exception:  # pragma: no cover - optional dependency
    pass
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
        """TODO: Add docstring."""
        config = load_config(api_key=api_key, security_key=security_key, base_url=base_url)

        self.base_url = sanitize_base_url(config.base_url or DEFAULT_BASE_URL)
        self._base_url = httpx.URL(self.base_url)

        self.timeout = timeout if isinstance(timeout, httpx.Timeout) else httpx.Timeout(timeout)
        self.retries = retries
        self.backoff_factor = backoff_factor

        if auth:
            self.auth = auth
        else:
            self.auth = ApiKeyAuth(config.api_key or "", config.security_key or "")

        self._client = self._create_client(self.auth)
        self._tracer: Optional[Tracer] = None

        if tracer is not None:
            self._tracer = tracer
        elif trace is not None:
            self._tracer = trace.get_tracer(__name__)
        else:
            self._tracer = None

    def _create_client(self, auth: AuthStrategy) -> Any:
        """TODO: Add docstring."""
        raise NotImplementedError
