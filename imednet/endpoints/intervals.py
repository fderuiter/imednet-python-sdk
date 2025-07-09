"""Endpoint for managing intervals (visit definitions) in a study."""

from imednet.core.paginator import AsyncPaginator, Paginator  # noqa: F401
from imednet.endpoints._mixins import ListGetEndpoint
from imednet.models.intervals import Interval


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
