"""Endpoint for managing subjects in a study."""

from typing import Any

from imednet.core.paginator import Paginator  # noqa: F401
from imednet.endpoints.async_endpoint_mixin import AsyncEndpointMixin
from imednet.endpoints.paged_endpoint_mixin import PagedEndpointMixin
from imednet.endpoints.sync_endpoint_mixin import SyncEndpointMixin
from imednet.models.subjects import Subject


class SubjectsEndpoint(SyncEndpointMixin, AsyncEndpointMixin, PagedEndpointMixin):
    """API endpoint for interacting with subjects in an iMedNet study."""

    PATH = "/api/v1/edc/studies"
    MODEL = Subject
    PATH_SUFFIX = "subjects"
    ID_FILTER = "subjectKey"
    INCLUDE_STUDY_IN_FILTER = True

    def list(self, study_key: str | None = None, **filters: Any) -> list[Subject]:
        """List subjects in a study with optional filtering."""
        return super().list(study_key=study_key, **filters)

    def get(self, study_key: str, subject_key: str) -> Subject:  # type: ignore[override]
        """Get a specific subject by key."""
        return super().get(subject_key, study_key=study_key)
