"""Endpoint for managing variables (data points on eCRFs) in a study."""

from typing import Any, List, Optional

from imednet.core.paginator import Paginator  # noqa: F401
from imednet.endpoints.async_endpoint_mixin import AsyncEndpointMixin
from imednet.endpoints.paged_endpoint_mixin import PagedEndpointMixin
from imednet.endpoints.sync_endpoint_mixin import SyncEndpointMixin
from imednet.models.variables import Variable


class VariablesEndpoint(SyncEndpointMixin, AsyncEndpointMixin, PagedEndpointMixin):
    """API endpoint for interacting with variables in an iMedNet study."""

    PATH = "/api/v1/edc/studies"
    MODEL = Variable
    PATH_SUFFIX = "variables"
    ID_FILTER = "variableId"
    PAGE_SIZE = 500
    CACHE_ENABLED = True

    def list(
        self, study_key: Optional[str] = None, refresh: bool = False, **filters: Any
    ) -> List[Variable]:
        """List variables in a study with optional filtering."""
        return super().list(study_key=study_key, refresh=refresh, **filters)

    def get(self, study_key: str, variable_id: int) -> Variable:  # type: ignore[override]
        """Get a specific variable by ID."""
        return super().get(variable_id, study_key=study_key)
