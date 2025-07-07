"""Endpoint for managing variables (data points on eCRFs) in a study."""

from typing import Any, Dict, List, Optional

from imednet.core.async_client import AsyncClient
from imednet.core.client import Client
from imednet.core.context import Context
from imednet.core.paginator import AsyncPaginator, Paginator  # noqa: F401
from imednet.endpoints._mixins import ListGetEndpoint
from imednet.models.variables import Variable


class VariablesEndpoint(ListGetEndpoint):
    """
    API endpoint for interacting with variables (data points on eCRFs) in an iMedNet study.

    Provides methods to list and retrieve individual variables.
    """

    PATH = "variables"
    MODEL = Variable
    _id_param = "variableId"
    _cache_name = "_variables_cache"
    PAGE_SIZE = 500
    _pop_study_filter = True
    _missing_study_exception = KeyError

    def __init__(
        self,
        client: Client,
        ctx: Context,
        async_client: AsyncClient | None = None,
    ) -> None:
        super().__init__(client, ctx, async_client)
        self._variables_cache: Dict[str, List[Variable]] = {}

    def list(  # type: ignore[override]
        self, study_key: Optional[str] = None, refresh: bool = False, **filters
    ) -> List[Variable]:
        """List variables in a study with optional filtering."""
        result = self._list_common(
            False,
            study_key=study_key,
            refresh=refresh,
            **filters,
        )
        return result  # type: ignore[return-value]

    async def async_list(  # type: ignore[override]
        self, study_key: Optional[str] = None, refresh: bool = False, **filters: Any
    ) -> List[Variable]:
        """Asynchronous version of :meth:`list`."""
        result = await self._list_common(
            True,
            study_key=study_key,
            refresh=refresh,
            **filters,
        )
        return result

    def get(self, study_key: str, variable_id: int) -> Variable:  # type: ignore[override]
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
        result = self._get_common(False, study_key=study_key, item_id=variable_id)
        return result  # type: ignore[return-value]

    async def async_get(self, study_key: str, variable_id: int) -> Variable:  # type: ignore[override]
        """Asynchronous version of :meth:`get`.

        ``refresh=True`` is also passed to :meth:`async_list` to bypass the
        cache.
        """
        return await self._get_common(True, study_key=study_key, item_id=variable_id)
