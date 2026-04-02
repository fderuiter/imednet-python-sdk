"""Endpoint for managing visits (interval instances) in a study."""

from imednet.core.endpoint.base import GenericEndpoint
from imednet.core.endpoint.edc_mixin import EdcEndpointMixin
from imednet.core.endpoint.mixins import FilterGetEndpointMixin, ListEndpointMixin
from imednet.models.visits import Visit


class VisitsEndpoint(
    EdcEndpointMixin,
    GenericEndpoint[Visit],
    ListEndpointMixin[Visit],
    FilterGetEndpointMixin[Visit],
):
    """
    API endpoint for interacting with visits (interval instances) in an iMedNet study.

    Provides methods to list and retrieve individual visits.
    """

    PATH = "visits"
    MODEL = Visit
    _id_param = "visitId"
