"""Endpoint for managing queries (dialogue/questions) in a study."""

from ..core.paginator import AsyncPaginator, Paginator  # noqa: F401
from ..models.queries import Query
from ._mixins import ListGetEndpoint
from .registry import register_endpoint


@register_endpoint("queries")
class QueriesEndpoint(ListGetEndpoint):
    """
    API endpoint for interacting with queries (dialogue/questions) in an iMedNet study.

    Provides methods to list and retrieve queries.
    """

    PATH = "queries"
    MODEL = Query
    _id_param = "annotationId"
