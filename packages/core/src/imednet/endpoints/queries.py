"""Endpoint for managing queries (dialogue/questions) in a study."""

from imednet.core.endpoint.edc_mixin import EdcAsyncListGetEndpoint, EdcSyncListGetEndpoint
from imednet.models.queries import Query


class QueriesOperationDef:
    """Definition for Query operations."""

    PATH = "queries"
    MODEL = Query
    _id_param = "annotationId"


class QueriesMixin(QueriesOperationDef):
    """Mixin for Queries operations."""

class QueriesEndpoint(QueriesMixin, EdcSyncListGetEndpoint[Query]):  # type: ignore[misc]
    """Synchronous endpoint for managing Queries."""

    pass


class AsyncQueriesEndpoint(QueriesMixin, EdcAsyncListGetEndpoint[Query]):  # type: ignore[misc]
    """Asynchronous endpoint for managing Queries."""

    pass
