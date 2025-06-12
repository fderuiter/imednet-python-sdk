"""Endpoint for managing forms (eCRFs) in a study."""

from typing import Any, Dict, List, Optional

from imednet.core.paginator import AsyncPaginator, Paginator
from imednet.endpoints.base import BaseEndpoint
from imednet.models.forms import Form
from imednet.utils.filters import build_filter_string


class FormsEndpoint(BaseEndpoint):
    """
    API endpoint for interacting with forms (eCRFs) in an iMedNet study.

    Provides methods to list and retrieve individual forms.
    """

    path = "/api/v1/edc/studies"

    def list(self, study_key: Optional[str] = None, **filters) -> List[Form]:
        """
        List forms in a study with optional filtering.

        Args:
            study_key: Study identifier (uses default from context if not specified)
            **filters: Additional filter parameters

        Returns:
            List of Form objects
        """
        filters = self._auto_filter(filters)
        if study_key:
            filters["studyKey"] = study_key

        study = filters.pop("studyKey")
        if not study:
            raise ValueError("Study key must be provided or set in the context")

        params: Dict[str, Any] = {}
        if filters:
            params["filter"] = build_filter_string(filters)

        path = self._build_path(study, "forms")
        paginator = Paginator(self._client, path, params=params, page_size=500)
        return [Form.from_json(item) for item in paginator]

    async def async_list(self, study_key: Optional[str] = None, **filters: Any) -> List[Form]:
        """Asynchronous version of :meth:`list`."""
        if self._async_client is None:
            raise RuntimeError("Async client not configured")
        filters = self._auto_filter(filters)
        if study_key:
            filters["studyKey"] = study_key

        study = filters.pop("studyKey")
        if not study:
            raise ValueError("Study key must be provided or set in the context")

        params: Dict[str, Any] = {}
        if filters:
            params["filter"] = build_filter_string(filters)

        path = self._build_path(study, "forms")
        paginator = AsyncPaginator(self._async_client, path, params=params, page_size=500)
        return [Form.from_json(item) async for item in paginator]

    def get(self, study_key: str, form_id: int) -> Form:
        """
        Get a specific form by ID.

        Args:
            study_key: Study identifier
            form_id: Form identifier

        Returns:
            Form object
        """
        path = self._build_path(study_key, "forms", form_id)
        raw = self._client.get(path).json().get("data", [])
        if not raw:
            raise ValueError(f"Form {form_id} not found in study {study_key}")
        return Form.from_json(raw[0])

    async def async_get(self, study_key: str, form_id: int) -> Form:
        """Asynchronous version of :meth:`get`."""
        if self._async_client is None:
            raise RuntimeError("Async client not configured")
        path = self._build_path(study_key, "forms", form_id)
        raw = (await self._async_client.get(path)).json().get("data", [])
        if not raw:
            raise ValueError(f"Form {form_id} not found in study {study_key}")
        return Form.from_json(raw[0])
