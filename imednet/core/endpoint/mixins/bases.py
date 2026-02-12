from __future__ import annotations

from typing import Any, Awaitable, List, Optional, cast

from imednet.core.paginator import AsyncPaginator, Paginator
from imednet.core.protocols import AsyncRequestorProtocol, RequestorProtocol

from ..base import BaseEndpoint
from .get import FilterGetEndpointMixin, PathGetEndpointMixin
from .list import ListEndpointMixin
from .parsing import T


class ListGetEndpointMixin(ListEndpointMixin[T], FilterGetEndpointMixin[T]):
    """Mixin implementing ``list`` and ``get`` helpers."""

    pass


class ListEndpoint(BaseEndpoint, ListEndpointMixin[T]):
    """Endpoint base class implementing ``list`` helpers."""

    PAGINATOR_CLS: type[Paginator] = Paginator
    ASYNC_PAGINATOR_CLS: type[AsyncPaginator] = AsyncPaginator

    def _get_context(
        self, is_async: bool
    ) -> tuple[RequestorProtocol | AsyncRequestorProtocol, type[Paginator] | type[AsyncPaginator]]:
        if is_async:
            return self._require_async_client(), self.ASYNC_PAGINATOR_CLS
        return self._client, self.PAGINATOR_CLS

    def _list_common(self, is_async: bool, **kwargs: Any) -> List[T] | Awaitable[List[T]]:
        client, paginator = self._get_context(is_async)
        return self._list_impl(client, paginator, **kwargs)

    def list(self, study_key: Optional[str] = None, **filters: Any) -> List[T]:
        return cast(List[T], self._list_common(False, study_key=study_key, **filters))

    async def async_list(self, study_key: Optional[str] = None, **filters: Any) -> List[T]:
        return await cast(
            Awaitable[List[T]], self._list_common(True, study_key=study_key, **filters)
        )


class ListGetEndpoint(ListEndpoint[T], FilterGetEndpointMixin[T]):
    """Endpoint base class implementing ``list`` and ``get`` helpers."""

    def _get_common(
        self,
        is_async: bool,
        *,
        study_key: Optional[str],
        item_id: Any,
    ) -> T | Awaitable[T]:
        client, paginator = self._get_context(is_async)
        return self._get_impl(client, paginator, study_key=study_key, item_id=item_id)

    def get(self, study_key: Optional[str], item_id: Any) -> T:
        return cast(T, self._get_common(False, study_key=study_key, item_id=item_id))

    async def async_get(self, study_key: Optional[str], item_id: Any) -> T:
        return await cast(
            Awaitable[T], self._get_common(True, study_key=study_key, item_id=item_id)
        )


class ListPathGetEndpoint(ListEndpoint[T], PathGetEndpointMixin[T]):
    """Endpoint base class implementing ``list`` and ``get`` (via path) helpers."""

    def get(self, study_key: Optional[str], item_id: Any) -> T:
        return cast(T, self._get_impl_path(self._client, study_key=study_key, item_id=item_id))

    async def async_get(self, study_key: Optional[str], item_id: Any) -> T:
        client = self._require_async_client()
        return await cast(
            Awaitable[T],
            self._get_impl_path(client, study_key=study_key, item_id=item_id, is_async=True),
        )
