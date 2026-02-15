from __future__ import annotations

from typing import Any, Awaitable, List, Optional

from imednet.core.paginator import AsyncPaginator, Paginator
from imednet.core.protocols import AsyncRequestorProtocol, RequestorProtocol

from ..base import BaseEndpoint
from ..operations import GetOperationMixin, ListOperationMixin
from .get import FilterGetEndpointMixin, PathGetEndpointMixin
from .list import ListEndpointMixin
from .parsing import T


class ListGetEndpointMixin(ListEndpointMixin[T], FilterGetEndpointMixin[T]):
    """Mixin implementing ``list`` and ``get`` helpers."""

    pass


class ListEndpoint(BaseEndpoint, ListEndpointMixin[T], ListOperationMixin[T]):
    """Endpoint base class implementing ``list`` helpers."""

    PAGINATOR_CLS: type[Paginator] = Paginator
    ASYNC_PAGINATOR_CLS: type[AsyncPaginator] = AsyncPaginator

    def _get_context(
        self, is_async: bool
    ) -> tuple[RequestorProtocol | AsyncRequestorProtocol, type[Paginator] | type[AsyncPaginator]]:
        if is_async:
            return self._require_async_client(), self.ASYNC_PAGINATOR_CLS
        return self._client, self.PAGINATOR_CLS

    def _execute_list(
        self, is_async: bool, study_key: Optional[str] = None, **filters: Any
    ) -> List[T] | Awaitable[List[T]]:
        client, paginator = self._get_context(is_async)
        return self._list_impl(client, paginator, study_key=study_key, **filters)


class ListGetEndpoint(ListEndpoint[T], FilterGetEndpointMixin[T], GetOperationMixin[T]):
    """Endpoint base class implementing ``list`` and ``get`` helpers."""

    def _execute_get(
        self,
        is_async: bool,
        study_key: Optional[str],
        item_id: Any,
    ) -> T | Awaitable[T]:
        client, paginator = self._get_context(is_async)
        return self._get_impl(client, paginator, study_key=study_key, item_id=item_id)


class ListPathGetEndpoint(ListEndpoint[T], PathGetEndpointMixin[T], GetOperationMixin[T]):
    """Endpoint base class implementing ``list`` and ``get`` (via path) helpers."""

    def _execute_get(
        self,
        is_async: bool,
        study_key: Optional[str],
        item_id: Any,
    ) -> T | Awaitable[T]:
        client: RequestorProtocol | AsyncRequestorProtocol
        if is_async:
            client = self._require_async_client()
        else:
            client = self._client
        return self._get_impl_path(
            client, study_key=study_key, item_id=item_id, is_async=is_async
        )


class StrictListGetEndpoint(ListGetEndpoint[T]):
    """
    Endpoint base class enforcing strict study key requirements.

    Populates study key from filters and raises KeyError if missing.
    """

    _pop_study_filter = True
    _missing_study_exception = KeyError


class MetadataListGetEndpoint(StrictListGetEndpoint[T]):
    """
    Endpoint base class for metadata resources.

    Inherits strict study key requirements and sets a larger default page size.
    """

    PAGE_SIZE = 500
