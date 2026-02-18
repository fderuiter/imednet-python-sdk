from __future__ import annotations

from typing import Any, Awaitable, List, Optional, cast

from imednet.core.endpoint.base import GenericEndpoint
from imednet.core.endpoint.edc_mixin import EdcEndpointMixin
from imednet.core.paginator import AsyncPaginator, Paginator
from imednet.core.protocols import AsyncRequestorProtocol, RequestorProtocol

from .get import FilterGetEndpointMixin, PathGetEndpointMixin
from .list import ListEndpointMixin
from .parsing import T


class ListGetEndpointMixin(ListEndpointMixin[T], FilterGetEndpointMixin[T]):
    """Mixin implementing ``list`` and ``get`` helpers."""

    pass


class GenericListEndpoint(GenericEndpoint[T], ListEndpointMixin[T]):
    """Generic endpoint implementing ``list`` helpers."""

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


class EdcListEndpoint(EdcEndpointMixin, GenericListEndpoint[T]):
    """EDC-specific list endpoint."""

    pass


class ListEndpoint(EdcListEndpoint[T]):
    """Endpoint base class implementing ``list`` helpers (Legacy)."""

    pass


class GenericListGetEndpoint(GenericListEndpoint[T], FilterGetEndpointMixin[T]):
    """Generic endpoint implementing ``list`` and ``get`` helpers."""

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


class EdcListGetEndpoint(EdcEndpointMixin, GenericListGetEndpoint[T]):
    """EDC-specific list/get endpoint."""

    pass


class ListGetEndpoint(EdcListGetEndpoint[T]):
    """Endpoint base class implementing ``list`` and ``get`` helpers (Legacy)."""

    pass


class GenericListPathGetEndpoint(GenericListEndpoint[T], PathGetEndpointMixin[T]):
    """Generic endpoint implementing ``list`` and ``get`` (via path) helpers."""

    def get(self, study_key: Optional[str], item_id: Any) -> T:
        return cast(T, self._get_impl_path(self._client, study_key=study_key, item_id=item_id))

    async def async_get(self, study_key: Optional[str], item_id: Any) -> T:
        client = self._require_async_client()
        return await cast(
            Awaitable[T],
            self._get_impl_path(client, study_key=study_key, item_id=item_id, is_async=True),
        )


class EdcListPathGetEndpoint(EdcEndpointMixin, GenericListPathGetEndpoint[T]):
    """EDC-specific list/path-get endpoint."""

    pass


class ListPathGetEndpoint(EdcListPathGetEndpoint[T]):
    """Endpoint base class implementing ``list`` and ``get`` (via path) helpers (Legacy)."""

    pass


class EdcStrictListGetEndpoint(EdcListGetEndpoint[T]):
    """
    Endpoint base class enforcing strict study key requirements (EDC).

    Populates study key from filters and raises KeyError if missing.
    """

    _pop_study_filter = True
    _missing_study_exception = KeyError


class StrictListGetEndpoint(EdcStrictListGetEndpoint[T]):
    """Endpoint base class enforcing strict study key requirements (Legacy)."""

    pass


class EdcMetadataListGetEndpoint(EdcStrictListGetEndpoint[T]):
    """
    Endpoint base class for metadata resources (EDC).

    Inherits strict study key requirements and sets a larger default page size.
    """

    PAGE_SIZE = 500


class MetadataListGetEndpoint(EdcMetadataListGetEndpoint[T]):
    """Endpoint base class for metadata resources (Legacy)."""

    pass
