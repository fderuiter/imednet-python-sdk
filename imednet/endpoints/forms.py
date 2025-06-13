"""Endpoint for managing forms (eCRFs) in a study."""

from typing import Any, Dict, List, Optional

from imednet.core.async_client import AsyncClient
from imednet.core.client import Client
from imednet.core.context import Context
from imednet.core.paginator import AsyncPaginator, Paginator
from imednet.endpoints.base import BaseEndpoint
from imednet.models.forms import Form
from imednet.utils.filters import build_filter_string


class FormsEndpoint(BaseEndpoint):
    """
    API endpoint for interacting with forms (eCRFs) in an iMedNet study.

    Provides methods to list and retrieve individual forms.
    """

    PATH = "/api/v1/edc/studies"

    def __init__(
        self,
        client: Client,
        ctx: Context,
        async_client: AsyncClient | None = None,
    ) -> None:
        super().__init__(client, ctx, async_client)
        self._forms_cache: Dict[str, List[Form]] = {}

    def list(
        self,
        study_key: Optional[str] = None,
        refresh: bool = False,
        **filters: Any,
    ) -> List[Form]:
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
        if not filters and not refresh and study in self._forms_cache:
            return self._forms_cache[study]

        params: Dict[str, Any] = {}
        if filters:
            params["filter"] = build_filter_string(filters)

        path = self._build_path(study, "forms")
        paginator = Paginator(self._client, path, params=params, page_size=500)
        result = [Form.from_json(item) for item in paginator]
        if not filters:
            self._forms_cache[study] = result
        return result

    async def async_list(
        self,
        study_key: Optional[str] = None,
        refresh: bool = False,
        **filters: Any,
    ) -> List[Form]:
        """Asynchronous version of :meth:`list`."""
        if self._async_client is None:
            raise RuntimeError("Async client not configured")
        filters = self._auto_filter(filters)
        if study_key:
            filters["studyKey"] = study_key

        study = filters.pop("studyKey")
        if not study:
            raise ValueError("Study key must be provided or set in the context")
        if not filters and not refresh and study in self._forms_cache:
            return self._forms_cache[study]

        params: Dict[str, Any] = {}
        if filters:
            params["filter"] = build_filter_string(filters)

        path = self._build_path(study, "forms")
        paginator = AsyncPaginator(self._async_client, path, params=params, page_size=500)
        result = [Form.from_json(item) async for item in paginator]
        if not filters:
            self._forms_cache[study] = result
        return result

    def get(self, study_key: str, form_id: int) -> Form:
        """
        Get a specific form by ID.

        Args:
            study_key: Study identifier
            form_id: Form identifier

        Returns:
            Form object
        """
        forms = self.list(study_key=study_key, refresh=True, formId=form_id)
        if not forms:
            raise ValueError(f"Form {form_id} not found in study {study_key}")
        return forms[0]

    async def async_get(self, study_key: str, form_id: int) -> Form:
        """Asynchronous version of :meth:`get`."""
        if self._async_client is None:
            raise RuntimeError("Async client not configured")
        forms = await self.async_list(study_key=study_key, refresh=True, formId=form_id)
        if not forms:
            raise ValueError(f"Form {form_id} not found in study {study_key}")
        return forms[0]
