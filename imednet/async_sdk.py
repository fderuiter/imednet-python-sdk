"""Asynchronous SDK entry point."""

from __future__ import annotations

from typing import Optional

from .core.async_client import AsyncClient
from .core.context import Context
from .endpoints.async_studies import AsyncStudiesEndpoint


class AsyncImednetSDK:
    """Async variant of :class:`imednet.sdk.ImednetSDK`."""

    def __init__(
        self,
        api_key: str,
        security_key: str,
        base_url: Optional[str] = None,
        timeout: float = 30.0,
        retries: int = 3,
        backoff_factor: float = 1.0,
    ) -> None:
        self.ctx = Context()
        self._client = AsyncClient(
            api_key=api_key,
            security_key=security_key,
            base_url=base_url,
            timeout=timeout,
            retries=retries,
            backoff_factor=backoff_factor,
        )
        self.studies = AsyncStudiesEndpoint(self._client, self.ctx)

    async def __aenter__(self) -> "AsyncImednetSDK":
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: object | None,
    ) -> None:
        await self.aclose()

    async def aclose(self) -> None:
        await self._client.aclose()
