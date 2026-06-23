"""Endpoint for managing queries (dialogue/questions) in a study."""

from imednet.core.endpoint.edc_mixin import ClientT, EdcListGetEndpoint
from imednet.models.queries import Query


class QueriesOperationDef:
    """TODO: Add docstring."""

    PATH = "queries"
    MODEL = Query
    _id_param = "annotationId"




    pass




    pass

class QueriesEndpoint(QueriesOperationDef, EdcListGetEndpoint[Query, ClientT]):  # type: ignore[misc]
    """TODO: Add docstring."""

    pass

class AsyncQueriesEndpoint(QueriesEndpoint):  # type: ignore[misc]
    """Legacy backwards-compatible async endpoint."""
    def __init__(self, client, ctx=None):
        """TODO: Add docstring."""
        super().__init__(client, ctx=ctx)
        self._async_client = client
