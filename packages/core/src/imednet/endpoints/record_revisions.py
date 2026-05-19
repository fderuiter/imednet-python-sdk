"""Endpoint for retrieving record revision history in a study."""

from imednet.core.endpoint.edc_mixin import EdcAsyncListGetEndpoint, EdcSyncListGetEndpoint
from imednet.models.record_revisions import RecordRevision


class RecordRevisionsEndpoint(EdcSyncListGetEndpoint[RecordRevision]):
    """
    API endpoint for accessing record revision history in an iMedNet study.

    Provides methods to list and retrieve record revisions.
    """

    PATH = "recordRevisions"
    MODEL = RecordRevision
    _id_param = "recordRevisionId"


class AsyncRecordRevisionsEndpoint(EdcAsyncListGetEndpoint[RecordRevision]):
    PATH = "recordRevisions"
    MODEL = RecordRevision
    _id_param = "recordRevisionId"
