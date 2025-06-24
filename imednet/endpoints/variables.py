"""Endpoint for managing variables (data points on eCRFs) in a study."""

import inspect
from typing import Any, Dict, List, Optional

from imednet.core.async_client import AsyncClient
from imednet.core.client import Client
from imednet.core.context import Context
from imednet.core.paginator import AsyncPaginator, Paginator
from imednet.endpoints.base import BaseEndpoint
from imednet.models.variables import Variable
from imednet.utils.filters import build_filter_string


class VariablesEndpoint(BaseEndpoint):
    """
    API endpoint for interacting with variables (data points on eCRFs) in an iMedNet study.

    Provides methods to list and retrieve individual variables.
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
        if not filters and not refresh and study in self._variables_cache:
            return self._variables_cache[study]

        params: Dict[str, Any] = {}
        if filters:
            params["filter"] = build_filter_string(filters)

        path = self._build_path(study, "variables")
        paginator = paginator_cls(client, path, params=params, page_size=500)

        if hasattr(paginator, "__aiter__"):

            async def _collect() -> List[Variable]:
                result = [Variable.from_json(item) async for item in paginator]
                if not filters:
                    self._variables_cache[study] = result
                return result

            return _collect()

        result = [Variable.from_json(item) for item in paginator]
        if not filters:
            self._variables_cache[study] = result
        return result

    def _get_impl(
        self, client: Any, paginator_cls: type[Any], study_key: str, variable_id: int
    ) -> Any:
        result = self._list_impl(
            client,
            paginator_cls,
            study_key=study_key,
            refresh=True,
            variableId=variable_id,
        )

        if inspect.isawaitable(result):

            async def _await() -> Variable:
                items = await result
                if not items:
                    raise ValueError(f"Variable {variable_id} not found in study {study_key}")
                return items[0]

            return _await()

        if not result:
            raise ValueError(f"Variable {variable_id} not found in study {study_key}")
        return result[0]

    def __init__(
        self,
        client: Client,
        ctx: Context,
        async_client: AsyncClient | None = None,
    ) -> None:
        super().__init__(client, ctx, async_client)
        self._variables_cache: Dict[str, List[Variable]] = {}

    def list(
        self, study_key: Optional[str] = None, refresh: bool = False, **filters
    ) -> List[Variable]:
        """List variables in a study with optional filtering."""
        result = self._list_impl(
            self._client,
            Paginator,
            study_key=study_key,
            refresh=refresh,
            **filters,
        )
        return result  # type: ignore[return-value]

    async def async_list(
        self, study_key: Optional[str] = None, refresh: bool = False, **filters: Any
    ) -> List[Variable]:
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

    def get(self, study_key: str, variable_id: int) -> Variable:
        """
        Get a specific variable by ID.

        The variables list is cached, so ``refresh=True`` is used when
        calling :meth:`list` to retrieve the latest data.

        Args:
            study_key: Study identifier
            variable_id: Variable identifier

        Returns:
            Variable object
        """
        result = self._get_impl(self._client, Paginator, study_key, variable_id)
        return result  # type: ignore[return-value]

    async def async_get(self, study_key: str, variable_id: int) -> Variable:
        """Asynchronous version of :meth:`get`.

        ``refresh=True`` is also passed to :meth:`async_list` to bypass the
        cache.
        """
        if self._async_client is None:
            raise RuntimeError("Async client not configured")
        return await self._get_impl(self._async_client, AsyncPaginator, study_key, variable_id)
