"""Endpoint for retrieving record revision history in a study."""

from imednet.core.endpoint.base import GenericEndpoint
from imednet.core.endpoint.edc_mixin import EdcEndpointMixin
from imednet.core.endpoint.mixins import FilterGetEndpointMixin, ListEndpointMixin
from imednet.models.record_revisions import RecordRevision


class RecordRevisionsEndpoint(
    EdcEndpointMixin,
    GenericEndpoint[RecordRevision],
    ListEndpointMixin[RecordRevision],
    FilterGetEndpointMixin[RecordRevision],
):
    """
    API endpoint for accessing record revision history in an iMedNet study.

    Provides methods to list and retrieve record revisions.
    """

    PATH = "recordRevisions"
    MODEL = RecordRevision
    _id_param = "recordRevisionId"
