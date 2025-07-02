"""Endpoint for managing codings (medical coding) in a study."""

from typing import Any

from imednet.core.paginator import Paginator  # noqa: F401
from imednet.endpoints.async_endpoint_mixin import AsyncEndpointMixin
from imednet.endpoints.paged_endpoint_mixin import PagedEndpointMixin
from imednet.endpoints.sync_endpoint_mixin import SyncEndpointMixin
from imednet.models.codings import Coding


class CodingsEndpoint(SyncEndpointMixin, AsyncEndpointMixin, PagedEndpointMixin):
    """API endpoint for interacting with codings in an iMedNet study."""

    PATH = "/api/v1/edc/studies"
    MODEL = Coding
    PATH_SUFFIX = "codings"
    ID_FILTER = "codingId"

    def list(self, study_key: str | None = None, **filters: Any) -> list[Coding]:
        """List codings in a study with optional filtering."""
        return super().list(study_key=study_key, **filters)

    def get(self, study_key: str, coding_id: str) -> Coding:  # type: ignore[override]
        """Get a specific coding by ID."""
        return super().get(coding_id, study_key=study_key)
