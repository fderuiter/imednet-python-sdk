"""Endpoint for managing intervals (visit definitions) in a study."""

from imednet.core.endpoint.base import GenericListGetEndpoint
from imednet.core.endpoint.edc_mixin import EdcEndpointMixin
from imednet.core.endpoint.mixins import CachedEndpointMixin
from imednet.core.endpoint.strategies import PopStudyKeyStrategy
from imednet.errors import ClientError
from imednet.models.intervals import Interval


class IntervalsEndpoint(
    EdcEndpointMixin,
    CachedEndpointMixin,
    GenericListGetEndpoint[Interval],
):
    """
    API endpoint for interacting with intervals (visit definitions) in an iMedNet study.

    Provides methods to list and retrieve individual intervals.
    """

    PATH = "intervals"
    MODEL = Interval
    _id_param = "intervalId"
    STUDY_KEY_STRATEGY = PopStudyKeyStrategy(exception_cls=ClientError)
