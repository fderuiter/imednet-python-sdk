from __future__ import annotations

from imednet.core.endpoint.base import GenericEndpoint
from imednet.core.endpoint.edc_mixin import EdcEndpointMixin
from imednet.core.paginator import AsyncPaginator, Paginator  # noqa: F401

from .get import FilterGetEndpointMixin, PathGetEndpointMixin
from .list import ListEndpointMixin
from .parsing import T


class ListGetEndpointMixin(ListEndpointMixin[T], FilterGetEndpointMixin[T]):
    """Mixin implementing ``list`` and ``get`` helpers."""

    pass


class GenericListEndpoint(GenericEndpoint[T], ListEndpointMixin[T]):
    """Generic endpoint implementing ``list`` helpers."""

    pass


class EdcListEndpoint(EdcEndpointMixin, GenericListEndpoint[T]):
    """EDC-specific list endpoint."""

    pass


class ListEndpoint(EdcListEndpoint[T]):
    """Endpoint base class implementing ``list`` helpers (Legacy)."""

    pass


class GenericListGetEndpoint(GenericListEndpoint[T], FilterGetEndpointMixin[T]):
    """Generic endpoint implementing ``list`` and ``get`` helpers."""

    pass


class EdcListGetEndpoint(EdcEndpointMixin, GenericListGetEndpoint[T]):
    """EDC-specific list/get endpoint."""

    pass


class ListGetEndpoint(EdcListGetEndpoint[T]):
    """Endpoint base class implementing ``list`` and ``get`` helpers (Legacy)."""

    pass


class GenericListPathGetEndpoint(GenericListEndpoint[T], PathGetEndpointMixin[T]):
    """Generic endpoint implementing ``list`` and ``get`` (via path) helpers."""

    pass


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
