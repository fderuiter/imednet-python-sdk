"""Endpoint for managing studies in the iMedNet system."""

from typing import Any, List

from imednet.core.paginator import Paginator  # noqa: F401
from imednet.endpoints.async_endpoint_mixin import AsyncEndpointMixin
from imednet.endpoints.paged_endpoint_mixin import PagedEndpointMixin
from imednet.endpoints.sync_endpoint_mixin import SyncEndpointMixin
from imednet.models.studies import Study


class StudiesEndpoint(SyncEndpointMixin, AsyncEndpointMixin, PagedEndpointMixin):
    """API endpoint for interacting with studies in the iMedNet system."""

    PATH = "/api/v1/edc/studies"
    MODEL = Study
    ID_FILTER = "studyKey"
    CACHE_ENABLED = True

    def list(self, refresh: bool = False, **filters: Any) -> List[Study]:
        """List studies with optional filtering."""
        return super().list(refresh=refresh, **filters)

    def get(self, study_key: str) -> Study:  # type: ignore[override]
        """Get a specific study by key."""
        return super().get(study_key)
