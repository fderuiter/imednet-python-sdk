"""Endpoint for managing sites (study locations) in a study."""

from typing import Any

from imednet.core.paginator import Paginator  # noqa: F401
from imednet.endpoints.async_endpoint_mixin import AsyncEndpointMixin
from imednet.endpoints.paged_endpoint_mixin import PagedEndpointMixin
from imednet.endpoints.sync_endpoint_mixin import SyncEndpointMixin
from imednet.models.sites import Site


class SitesEndpoint(SyncEndpointMixin, AsyncEndpointMixin, PagedEndpointMixin):
    """API endpoint for interacting with sites in an iMedNet study."""

    PATH = "/api/v1/edc/studies"
    MODEL = Site
    PATH_SUFFIX = "sites"
    ID_FILTER = "siteId"

    def list(self, study_key: str | None = None, **filters: Any) -> list[Site]:
        """List sites in a study with optional filtering."""
        return super().list(study_key=study_key, **filters)

    def get(self, study_key: str, site_id: int) -> Site:  # type: ignore[override]
        """Get a specific site by ID."""
        return super().get(site_id, study_key=study_key)
