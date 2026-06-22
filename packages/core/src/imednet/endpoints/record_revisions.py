"""Endpoint for retrieving record revision history in a study."""

from imednet.core.endpoint.edc_mixin import EdcAsyncListGetEndpoint, EdcSyncListGetEndpoint
from imednet.models.record_revisions import RecordRevision


class RecordRevisionsOperationDef:
    """TODO: Add docstring."""

    PATH = "recordRevisions"
    MODEL = RecordRevision
    _id_param = "recordRevisionId"


class RecordRevisionsEndpoint(RecordRevisionsOperationDef, EdcSyncListGetEndpoint[RecordRevision]):  # type: ignore[misc]
    """TODO: Add docstring."""

    pass


class AsyncRecordRevisionsEndpoint(  # type: ignore[misc]
    RecordRevisionsOperationDef, EdcAsyncListGetEndpoint[RecordRevision]
):
    """TODO: Add docstring."""

    pass
