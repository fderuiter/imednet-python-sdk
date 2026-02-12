"""Endpoint for managing queries (dialogue/questions) in a study."""

from imednet.core.endpoint.mixins import ListGetEndpoint
from imednet.core.endpoint.mixins.edc import EdcEndpointMixin
from imednet.models.queries import Query


class QueriesEndpoint(EdcEndpointMixin, ListGetEndpoint[Query]):
    """
    API endpoint for interacting with queries (dialogue/questions) in an iMedNet study.

    Provides methods to list and retrieve queries.
    """

    PATH = "queries"
    MODEL = Query
    _id_param = "annotationId"
