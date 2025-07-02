"""Endpoint for managing queries (dialogue/questions) in a study."""

from typing import Any

from imednet.core.paginator import Paginator  # noqa: F401
from imednet.endpoints.async_endpoint_mixin import AsyncEndpointMixin
from imednet.endpoints.paged_endpoint_mixin import PagedEndpointMixin
from imednet.endpoints.sync_endpoint_mixin import SyncEndpointMixin
from imednet.models.queries import Query


class QueriesEndpoint(SyncEndpointMixin, AsyncEndpointMixin, PagedEndpointMixin):
    """API endpoint for interacting with queries in an iMedNet study."""

    PATH = "/api/v1/edc/studies"
    MODEL = Query
    PATH_SUFFIX = "queries"
    ID_FILTER = "annotationId"
    INCLUDE_STUDY_IN_FILTER = True

    def list(self, study_key: str | None = None, **filters: Any) -> list[Query]:
        """List queries in a study with optional filtering."""
        return super().list(study_key=study_key, **filters)

    def get(self, study_key: str, annotation_id: int) -> Query:  # type: ignore[override]
        """Get a specific query by annotation ID."""
        return super().get(annotation_id, study_key=study_key)
