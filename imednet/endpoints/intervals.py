"""Endpoint for managing intervals (visit definitions) in a study."""

from imednet.core.endpoint.mixins import EdcMetadataListGetEndpoint
from imednet.models.intervals import Interval


class IntervalsEndpoint(EdcMetadataListGetEndpoint[Interval]):
    """
    API endpoint for interacting with intervals (visit definitions) in an iMedNet study.

    Provides methods to list and retrieve individual intervals.
    """

    PATH = "intervals"
    MODEL = Interval
    _id_param = "intervalId"
    _cache_name = "_intervals_cache"
