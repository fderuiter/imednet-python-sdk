"""Endpoint for retrieving record revision history in a study."""

from typing import Any

from imednet.core.paginator import Paginator  # noqa: F401
from imednet.endpoints.async_endpoint_mixin import AsyncEndpointMixin
from imednet.endpoints.paged_endpoint_mixin import PagedEndpointMixin
from imednet.endpoints.sync_endpoint_mixin import SyncEndpointMixin
from imednet.models.record_revisions import RecordRevision


class RecordRevisionsEndpoint(SyncEndpointMixin, AsyncEndpointMixin, PagedEndpointMixin):
    """API endpoint for accessing record revision history in an iMedNet study."""

    PATH = "/api/v1/edc/studies"
    MODEL = RecordRevision
    PATH_SUFFIX = "recordRevisions"
    ID_FILTER = "recordRevisionId"
    INCLUDE_STUDY_IN_FILTER = True

    def list(self, study_key: str | None = None, **filters: Any) -> list[RecordRevision]:
        """List record revisions in a study with optional filtering."""
        return super().list(study_key=study_key, **filters)

    def get(self, study_key: str, record_revision_id: int) -> RecordRevision:  # type: ignore[override]
        """Get a specific record revision by ID."""
        return super().get(record_revision_id, study_key=study_key)
