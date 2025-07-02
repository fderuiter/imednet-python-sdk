"""Endpoint for managing intervals (visit definitions) in a study."""

from typing import Any, List, Optional

from imednet.core.paginator import Paginator  # noqa: F401
from imednet.endpoints.async_endpoint_mixin import AsyncEndpointMixin
from imednet.endpoints.paged_endpoint_mixin import PagedEndpointMixin
from imednet.endpoints.sync_endpoint_mixin import SyncEndpointMixin
from imednet.models.intervals import Interval


class IntervalsEndpoint(SyncEndpointMixin, AsyncEndpointMixin, PagedEndpointMixin):
    """API endpoint for interacting with intervals in an iMedNet study."""

    PATH = "/api/v1/edc/studies"
    MODEL = Interval
    PATH_SUFFIX = "intervals"
    ID_FILTER = "intervalId"
    PAGE_SIZE = 500
    CACHE_ENABLED = True

    def list(
        self, study_key: Optional[str] = None, refresh: bool = False, **filters: Any
    ) -> List[Interval]:
        """List intervals in a study with optional filtering."""
        return super().list(study_key=study_key, refresh=refresh, **filters)

    def get(self, study_key: str, interval_id: int) -> Interval:  # type: ignore[override]
        """Get a specific interval by ID."""
        return super().get(interval_id, study_key=study_key)
