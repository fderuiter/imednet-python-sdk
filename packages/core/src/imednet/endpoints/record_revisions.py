"""Endpoint for retrieving record revision history in a study."""

from imednet.core.endpoint.edc_mixin import EdcAsyncListGetEndpoint, EdcSyncListGetEndpoint
from imednet.models.record_revisions import RecordRevision

class RecordRevisionsOperationDef:
    PATH = "recordRevisions"
    MODEL = RecordRevision
    _id_param = "recordRevisionId"

class RecordRevisionsEndpoint(RecordRevisionsOperationDef, EdcSyncListGetEndpoint[RecordRevision]): # type: ignore[misc]
    pass

class AsyncRecordRevisionsEndpoint(RecordRevisionsOperationDef, EdcAsyncListGetEndpoint[RecordRevision]): # type: ignore[misc]
    pass
