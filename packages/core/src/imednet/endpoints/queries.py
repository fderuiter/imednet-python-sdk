"""Endpoint for managing queries (dialogue/questions) in a study."""

from imednet.core.endpoint.edc_mixin import EdcAsyncListGetEndpoint, EdcSyncListGetEndpoint
from imednet.models.queries import Query


class QueriesOperationDef:
    """TODO: Add docstring."""

    PATH = "queries"
    MODEL = Query
    _id_param = "annotationId"


class QueriesEndpoint(QueriesOperationDef, EdcSyncListGetEndpoint[Query]):  # type: ignore[misc]
    """TODO: Add docstring."""

    pass


class AsyncQueriesEndpoint(QueriesOperationDef, EdcAsyncListGetEndpoint[Query]):  # type: ignore[misc]
    """TODO: Add docstring."""

    pass
