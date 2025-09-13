"""Endpoint for retrieving record revision history in a study."""

from ..core.paginator import AsyncPaginator, Paginator  # noqa: F401
from ..models.record_revisions import RecordRevision
from ._mixins import ListGetEndpoint
from .registry import register_endpoint


@register_endpoint("record_revisions")
class RecordRevisionsEndpoint(ListGetEndpoint):
    """
    API endpoint for accessing record revision history in an iMedNet study.

    Provides methods to list and retrieve record revisions.
    """

    PATH = "recordRevisions"
    MODEL = RecordRevision
    _id_param = "recordRevisionId"
