"""Endpoint for retrieving record revision history in a study."""

from imednet.core.endpoint.edc_mixin import ClientT, EdcListGetEndpoint
from imednet.models.record_revisions import RecordRevision


class RecordRevisionsOperationDef:
    """TODO: Add docstring."""

    PATH = "recordRevisions"
    MODEL = RecordRevision
    _id_param = "recordRevisionId"




    pass




    pass

class RecordRevisionsEndpoint(RecordRevisionsOperationDef, EdcListGetEndpoint[RecordRevision, ClientT]):  # type: ignore[misc]
    """TODO: Add docstring."""

    pass

class AsyncRecordRevisionsEndpoint(RecordRevisionsEndpoint):  # type: ignore[misc]
    """Legacy backwards-compatible async endpoint."""
    def __init__(self, client, ctx=None):
        """TODO: Add docstring."""
        super().__init__(client, ctx=ctx)
        self._async_client = client
