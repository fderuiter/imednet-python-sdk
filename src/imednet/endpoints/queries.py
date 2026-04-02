"""Endpoint for managing queries (dialogue/questions) in a study."""

from imednet.core.endpoint.base import GenericEndpoint
from imednet.core.endpoint.edc_mixin import EdcEndpointMixin
from imednet.core.endpoint.mixins import FilterGetEndpointMixin, ListEndpointMixin
from imednet.models.queries import Query


class QueriesEndpoint(
    EdcEndpointMixin,
    GenericEndpoint[Query],
    ListEndpointMixin[Query],
    FilterGetEndpointMixin[Query],
):
    """
    API endpoint for interacting with queries (dialogue/questions) in an iMedNet study.

    Provides methods to list and retrieve queries.
    """

    PATH = "queries"
    MODEL = Query
    _id_param = "annotationId"
