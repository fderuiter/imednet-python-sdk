from __future__ import annotations

import logging
from typing import Any, Awaitable, Callable, Optional, Type, Union

import httpx
from tenacity import RetryCallState

from ._requester import RequestExecutor
from .base_client import BaseClient, Tracer

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
    def _should_retry(self) -> Callable[[RetryCallState], bool]:
        return self._executor.should_retry or self._executor._default_should_retry

    @_should_retry.setter
    def _should_retry(self, func: Callable[[RetryCallState], bool]) -> None:
        self._executor.should_retry = func

    def _request(
        self, method: str, path: str, **kwargs: Any
    ) -> Awaitable[httpx.Response] | httpx.Response:
        return self._executor(method, path, **kwargs)
