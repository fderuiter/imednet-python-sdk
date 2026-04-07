"""Endpoint for managing intervals (visit definitions) in a study."""

from imednet.core.endpoint.base import GenericEndpoint
from imednet.core.endpoint.edc_mixin import EdcEndpointMixin
from imednet.core.endpoint.mixins import FilterGetEndpointMixin, ListEndpointMixin
from imednet.core.endpoint.strategies import PopStudyKeyStrategy
from imednet.models.intervals import Interval


class IntervalsEndpoint(
    EdcEndpointMixin,
    GenericEndpoint[Interval],
    ListEndpointMixin[Interval],
    FilterGetEndpointMixin[Interval],
):
    """
    API endpoint for interacting with intervals (visit definitions) in an iMedNet study.

    Provides methods to list and retrieve individual intervals.
    """

    PATH = "intervals"
    MODEL = Interval
    _id_param = "intervalId"
    _enable_cache = True
    STUDY_KEY_STRATEGY = PopStudyKeyStrategy(exception_cls=KeyError)
    PAGE_SIZE = 500
