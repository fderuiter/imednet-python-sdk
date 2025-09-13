"""Endpoint for managing visits (interval instances) in a study."""

from ..core.paginator import AsyncPaginator, Paginator  # noqa: F401
from ..models.visits import Visit
from ._mixins import ListGetEndpoint
from .registry import register_endpoint


@register_endpoint("visits")
class VisitsEndpoint(ListGetEndpoint):
    """
    API endpoint for interacting with visits (interval instances) in an iMedNet study.

    Provides methods to list and retrieve individual visits.
    """

    PATH = "visits"
    MODEL = Visit
    _id_param = "visitId"
