"""Shared async helpers for endpoint wrappers."""

from __future__ import annotations

from typing import Any

from imednet.core.async_client import AsyncClient
from imednet.core.paginator import AsyncPaginator


class AsyncEndpointMixin:
    """Mixin providing async ``list`` and ``get`` helpers."""

    def _require_async_client(self: Any) -> AsyncClient:
        """Return the configured async client or raise a helpful error."""
        if self._async_client is None:
            raise RuntimeError("Async client not configured")
        return self._async_client

    async def async_list(self: Any, *args: Any, **kwargs: Any) -> Any:
        """Delegate to ``_list_impl`` using :class:`AsyncPaginator`."""
        if args:
            if len(args) == 1 and "study_key" not in kwargs:
                kwargs["study_key"] = args[0]
            else:
                raise TypeError("Invalid positional arguments")
        client = self._require_async_client()
        return await self._list_impl(client, AsyncPaginator, **kwargs)

    async def async_get(self: Any, identifier: Any, *args: Any, **kwargs: Any) -> Any:
        """Delegate to ``_get_impl`` using :class:`AsyncPaginator`."""
        if args:
            raise TypeError("Invalid positional arguments")
        client = self._require_async_client()
        return await self._get_impl(client, AsyncPaginator, identifier, **kwargs)
