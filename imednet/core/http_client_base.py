from __future__ import annotations

import logging
from typing import Any, Awaitable, Optional, Type, Union, cast

import httpx

from ._requester import RequestExecutor
from .base_client import BaseClient, Tracer
from .retry import RetryPolicy

logger = logging.getLogger(__name__)


class HTTPClientBase(BaseClient):
    """Shared logic for synchronous and asynchronous HTTP clients."""

    HTTPX_CLIENT_CLS: Type[httpx.Client | httpx.AsyncClient]
    IS_ASYNC: bool

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
        retry_policy: RetryPolicy | None = None,
    ) -> None:
        super().__init__(
            api_key=api_key,
            security_key=security_key,
            base_url=base_url,
            timeout=timeout,
            retries=retries,
            backoff_factor=backoff_factor,
            log_level=log_level,
            tracer=tracer,
        )
        self._executor = RequestExecutor(
            lambda *a, **kw: self._client.request(*a, **kw),
            is_async=self.IS_ASYNC,
            retries=self.retries,
            backoff_factor=self.backoff_factor,
            tracer=self._tracer,
            retry_policy=retry_policy,
        )

    def _create_client(self, api_key: str, security_key: str) -> httpx.Client | httpx.AsyncClient:
        return self.HTTPX_CLIENT_CLS(
            base_url=self.base_url,
            headers={
                "Accept": "application/json",
                "Content-Type": "application/json",
                "x-api-key": api_key,
                "x-imn-security-key": security_key,
            },
            timeout=self.timeout,
        )

    @property
    def retry_policy(self) -> RetryPolicy:
        return cast(RetryPolicy, self._executor.retry_policy)

    @retry_policy.setter
    def retry_policy(self, policy: RetryPolicy) -> None:
        self._executor.retry_policy = policy

    def _request(
        self, method: str, path: str, **kwargs: Any
    ) -> Awaitable[httpx.Response] | httpx.Response:
        return self._executor(method, path, **kwargs)
