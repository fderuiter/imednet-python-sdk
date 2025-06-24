"""Endpoint for managing forms (eCRFs) in a study."""

import inspect
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

    def _list_impl(
        self,
        client: Any,
        paginator_cls: type[Any],
        *,
        study_key: Optional[str] = None,
        refresh: bool = False,
        **filters: Any,
    ) -> Any:
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
        paginator = paginator_cls(client, path, params=params, page_size=500)

        if hasattr(paginator, "__aiter__"):

            async def _collect() -> List[Form]:
                result = [Form.from_json(item) async for item in paginator]
                if not filters:
                    self._forms_cache[study] = result
                return result

            return _collect()

        result = [Form.from_json(item) for item in paginator]
        if not filters:
            self._forms_cache[study] = result
        return result

    def _get_impl(self, client: Any, paginator_cls: type[Any], study_key: str, form_id: int) -> Any:
        result = self._list_impl(
            client,
            paginator_cls,
            study_key=study_key,
            refresh=True,
            formId=form_id,
        )

        if inspect.isawaitable(result):

            async def _await() -> Form:
                items = await result
                if not items:
                    raise ValueError(f"Form {form_id} not found in study {study_key}")
                return items[0]

            return _await()

        if not result:
            raise ValueError(f"Form {form_id} not found in study {study_key}")
        return result[0]

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
        """List forms in a study with optional filtering."""
        result = self._list_impl(
            self._client,
            Paginator,
            study_key=study_key,
            refresh=refresh,
            **filters,
        )
        return result  # type: ignore[return-value]

    async def async_list(
        self,
        study_key: Optional[str] = None,
        refresh: bool = False,
        **filters: Any,
    ) -> List[Form]:
        """Asynchronous version of :meth:`list`."""
        if self._async_client is None:
            raise RuntimeError("Async client not configured")
        result = await self._list_impl(
            self._async_client,
            AsyncPaginator,
            study_key=study_key,
            refresh=refresh,
            **filters,
        )
        return result

    def get(self, study_key: str, form_id: int) -> Form:
        """
        Get a specific form by ID.

        This endpoint caches form listings. ``refresh=True`` is used when
        calling :meth:`list` so that the most recent data is returned.

        Args:
            study_key: Study identifier
            form_id: Form identifier

        Returns:
            Form object
        """
        result = self._get_impl(self._client, Paginator, study_key, form_id)
        return result  # type: ignore[return-value]

    async def async_get(self, study_key: str, form_id: int) -> Form:
        """Asynchronous version of :meth:`get`.

        ``refresh=True`` is also passed to :meth:`async_list` to bypass the
        cache.
        """
        if self._async_client is None:
            raise RuntimeError("Async client not configured")
        return await self._get_impl(self._async_client, AsyncPaginator, study_key, form_id)
