from __future__ import annotations

from typing import Any, List, Optional

from imednet.core.endpoint.base import GenericEndpoint
from imednet.core.endpoint.edc_mixin import EdcEndpointMixin
from imednet.core.paginator import AsyncPaginator, Paginator

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

    def list(self, study_key: Optional[str] = None, **filters: Any) -> List[T]:
        return self._list_sync(
            self._require_sync_client(),
            self.PAGINATOR_CLS,
            study_key=study_key,
            **filters,
        )

    async def async_list(self, study_key: Optional[str] = None, **filters: Any) -> List[T]:
        client = self._require_async_client()
        return await self._list_async(
            client,
            self.ASYNC_PAGINATOR_CLS,
            study_key=study_key,
            **filters,
        )


class EdcListEndpoint(EdcEndpointMixin, GenericListEndpoint[T]):
    """EDC-specific list endpoint."""

    pass


class ListEndpoint(EdcListEndpoint[T]):
    """Endpoint base class implementing ``list`` helpers (Legacy)."""

    pass


class GenericListGetEndpoint(GenericListEndpoint[T], FilterGetEndpointMixin[T]):
    """Generic endpoint implementing ``list`` and ``get`` helpers."""

    def get(self, study_key: Optional[str], item_id: Any) -> T:
        return self._get_sync(
            self._require_sync_client(),
            self.PAGINATOR_CLS,
            study_key=study_key,
            item_id=item_id,
        )

    async def async_get(self, study_key: Optional[str], item_id: Any) -> T:
        client = self._require_async_client()
        return await self._get_async(
            client,
            self.ASYNC_PAGINATOR_CLS,
            study_key=study_key,
            item_id=item_id,
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
        return self._get_path_sync(
            self._require_sync_client(),
            study_key=study_key,
            item_id=item_id,
        )

    async def async_get(self, study_key: Optional[str], item_id: Any) -> T:
        client = self._require_async_client()
        return await self._get_path_async(
            client,
            study_key=study_key,
            item_id=item_id,
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
