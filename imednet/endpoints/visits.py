"""Endpoint for managing visits (interval instances) in a study."""

from typing import Any

from imednet.core.paginator import Paginator  # noqa: F401
from imednet.endpoints.async_endpoint_mixin import AsyncEndpointMixin
from imednet.endpoints.paged_endpoint_mixin import PagedEndpointMixin
from imednet.endpoints.sync_endpoint_mixin import SyncEndpointMixin
from imednet.models.visits import Visit


class VisitsEndpoint(SyncEndpointMixin, AsyncEndpointMixin, PagedEndpointMixin):
    """API endpoint for interacting with visits in an iMedNet study."""

    PATH = "/api/v1/edc/studies"
    MODEL = Visit
    PATH_SUFFIX = "visits"
    ID_FILTER = "visitId"
    INCLUDE_STUDY_IN_FILTER = True

    def list(self, study_key: str | None = None, **filters: Any) -> list[Visit]:
        """List visits in a study with optional filtering."""
        return super().list(study_key=study_key, **filters)

    def get(self, study_key: str, visit_id: int) -> Visit:  # type: ignore[override]
        """Get a specific visit by ID."""
        return super().get(visit_id, study_key=study_key)
