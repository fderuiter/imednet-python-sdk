"""Endpoint for managing variables (data points on eCRFs) in a study."""

from typing import Any, List, Optional

from imednet.core.paginator import AsyncPaginator, Paginator
from imednet.endpoints.base import BaseEndpoint
from imednet.models.variables import Variable
from imednet.utils.filters import build_filter_string as _build_filter_string

from ._mixins import ListGetEndpointMixin

# expose for patching in tests
build_filter_string = _build_filter_string


class VariablesEndpoint(ListGetEndpointMixin, BaseEndpoint):
    """
    API endpoint for interacting with variables (data points on eCRFs) in an iMedNet study.

    Provides methods to list and retrieve individual variables.
    """

    PATH = "variables"
    MODEL = Variable
    ID_FIELD = "variableId"
    _cache_name = "_variables_cache"
    _pop_study_key = True
    _page_size = 500

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
        result = self._get_impl(
            self._client,
            Paginator,
            study_key=study_key,
            item_id=variable_id,
        )
        return result  # type: ignore[return-value]

    async def async_get(self, study_key: str, variable_id: int) -> Variable:
        """Asynchronous version of :meth:`get`.

        ``refresh=True`` is also passed to :meth:`async_list` to bypass the
        cache.
        """
        if self._async_client is None:
            raise RuntimeError("Async client not configured")
        return await self._get_impl(
            self._async_client,
            AsyncPaginator,
            study_key=study_key,
            item_id=variable_id,
        )
