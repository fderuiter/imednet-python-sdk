"""Endpoint for managing forms (eCRFs) in a study."""

from typing import Any, List, Optional

from imednet.core.paginator import Paginator  # noqa: F401
from imednet.endpoints.async_endpoint_mixin import AsyncEndpointMixin
from imednet.endpoints.paged_endpoint_mixin import PagedEndpointMixin
from imednet.endpoints.sync_endpoint_mixin import SyncEndpointMixin
from imednet.models.forms import Form


class FormsEndpoint(SyncEndpointMixin, AsyncEndpointMixin, PagedEndpointMixin):
    """API endpoint for interacting with forms in an iMedNet study."""

    PATH = "/api/v1/edc/studies"
    MODEL = Form
    PATH_SUFFIX = "forms"
    ID_FILTER = "formId"
    PAGE_SIZE = 500
    CACHE_ENABLED = True

    def list(
        self,
        study_key: Optional[str] = None,
        refresh: bool = False,
        **filters: Any,
    ) -> List[Form]:
        """List forms in a study with optional filtering."""
        return super().list(study_key=study_key, refresh=refresh, **filters)

    def get(self, study_key: str, form_id: int) -> Form:  # type: ignore[override]
        """Get a specific form by ID."""
        return super().get(form_id, study_key=study_key)
