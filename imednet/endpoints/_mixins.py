from __future__ import annotations

from typing import TypeVar

from imednet.endpoints.base import BaseEndpoint
from imednet.endpoints.mixins import FilteredGetMixin

T = TypeVar("T", bound="JsonModel")

# Fix for circular import or simple typing issue if JsonModel is not imported
from imednet.models.json_base import JsonModel  # noqa: F401


class ListGetEndpointMixin(FilteredGetMixin[T]):
    """
    Mixin implementing ``list`` and ``get`` helpers.

    Deprecated: Use ``imednet.endpoints.mixins.FilteredGetMixin`` instead.
    """


class ListGetEndpoint(BaseEndpoint, ListGetEndpointMixin[T]):
    """Endpoint base class implementing ``list`` and ``get`` helpers."""
