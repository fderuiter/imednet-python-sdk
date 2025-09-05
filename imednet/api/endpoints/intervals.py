"""Endpoint for managing intervals (visit definitions) in a study."""

from ..core.paginator import AsyncPaginator, Paginator  # noqa: F401
from ..models.intervals import Interval
from ._mixins import ListGetEndpoint
from .registry import register_endpoint


@register_endpoint("intervals")
class IntervalsEndpoint(ListGetEndpoint):
    """
    API endpoint for interacting with intervals (visit definitions) in an iMedNet study.

    Provides methods to list and retrieve individual intervals.
    """

    PATH = "intervals"
    MODEL = Interval
    _id_param = "intervalId"
    _cache_name = "_intervals_cache"
    PAGE_SIZE = 500
    _pop_study_filter = True
