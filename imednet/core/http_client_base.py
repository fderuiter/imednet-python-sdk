from __future__ import annotations

import logging
from typing import Any, Awaitable, Optional, Type, Union, cast

import httpx

from imednet.auth.strategy import AuthStrategy
from imednet.constants import (
    CONTENT_TYPE_JSON,
    HEADER_ACCEPT,
    HEADER_CONTENT_TYPE,
)
from imednet.core.http.executor import BaseRequestExecutor

from .base_client import BaseClient, Tracer
from .retry import RetryPolicy

logger = logging.getLogger(__name__)


class HTTPClientBase(BaseClient):
    """Shared logic for synchronous and asynchronous HTTP clients."""

    HTTPX_CLIENT_CLS: Type[httpx.Client | httpx.AsyncClient]
    EXECUTOR_CLS: Type[BaseRequestExecutor]
    IS_ASYNC: bool

    def __init__(
        self,
        api_key: Optional[str] = None,
        security_key: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: Union[float, httpx.Timeout] = 30.0,
        retries: int = 3,
        backoff_factor: float = 1.0,
        tracer: Optional[Tracer] = None,
        retry_policy: RetryPolicy | None = None,
        auth: Optional[AuthStrategy] = None,
    ) -> None:
        super().__init__(
            api_key=api_key,
            security_key=security_key,
            base_url=base_url,
            timeout=timeout,
            retries=retries,
            backoff_factor=backoff_factor,
            tracer=tracer,
            auth=auth,
        )

        send_fn: Any
        if self.IS_ASYNC:

            async def send_async(method: str, url: str, **kwargs: Any) -> httpx.Response:
                return await self._client.request(method, url, **kwargs)

            send_fn = send_async
        else:

            def send_sync(method: str, url: str, **kwargs: Any) -> httpx.Response:
                return self._client.request(method, url, **kwargs)

            send_fn = send_sync

        self._executor = self.EXECUTOR_CLS(
            send=send_fn,
            retries=self.retries,
            backoff_factor=self.backoff_factor,
            tracer=self._tracer,
            retry_policy=retry_policy,
        )

    def _create_client(self, auth: AuthStrategy) -> httpx.Client | httpx.AsyncClient:
        headers = {
            HEADER_ACCEPT: CONTENT_TYPE_JSON,
            HEADER_CONTENT_TYPE: CONTENT_TYPE_JSON,
        }
        headers.update(auth.get_headers())

        return self.HTTPX_CLIENT_CLS(
            base_url=self.base_url,
            headers=headers,
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
