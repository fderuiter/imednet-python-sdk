"""Endpoint for managing queries (dialogue/questions) in a study."""

from imednet.core.endpoint.edc_mixin import EdcAsyncListGetEndpoint, EdcSyncListGetEndpoint
from imednet.models.queries import Query


class QueriesEndpoint(EdcSyncListGetEndpoint[Query]):
    """
    API endpoint for interacting with queries (dialogue/questions) in an iMedNet study.

    Provides methods to list and retrieve queries.
    """

    PATH = "queries"
    MODEL = Query
    _id_param = "annotationId"


class AsyncQueriesEndpoint(EdcAsyncListGetEndpoint[Query]):
    PATH = "queries"
    MODEL = Query
    _id_param = "annotationId"
