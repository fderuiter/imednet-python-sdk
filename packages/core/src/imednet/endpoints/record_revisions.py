"""Endpoint for retrieving record revision history in a study."""

from imednet.core.endpoint.edc_mixin import EdcGenericListGetEndpoint
from imednet.models.record_revisions import RecordRevision


class RecordRevisionsEndpoint(EdcGenericListGetEndpoint[RecordRevision]):
    """
    API endpoint for accessing record revision history in an iMedNet study.

    Provides methods to list and retrieve record revisions.
    """

    PATH = "recordRevisions"
    MODEL = RecordRevision
    _id_param = "recordRevisionId"
