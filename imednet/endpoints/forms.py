"""Endpoint for managing forms (eCRFs) in a study."""

from typing import Any, Dict, List, Optional

from imednet.core.async_client import AsyncClient
from imednet.core.client import Client
from imednet.core.context import Context
from imednet.core.paginator import AsyncPaginator, Paginator  # noqa: F401
from imednet.endpoints._mixins import ListGetEndpoint
from imednet.models.forms import Form


class FormsEndpoint(ListGetEndpoint):
    """
    API endpoint for interacting with forms (eCRFs) in an iMedNet study.

    Provides methods to list and retrieve individual forms.
    """

    PATH = "forms"
    MODEL = Form
    _id_param = "formId"
    _cache_name = "_forms_cache"
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
        self._forms_cache: Dict[str, List[Form]] = {}

    def list(  # type: ignore[override]
        self,
        study_key: Optional[str] = None,
        refresh: bool = False,
        **filters: Any,
    ) -> List[Form]:
        """List forms in a study with optional filtering."""
        result = self._list_common(
            False,
            study_key=study_key,
            refresh=refresh,
            **filters,
        )
        return result  # type: ignore[return-value]

    async def async_list(  # type: ignore[override]
        self,
        study_key: Optional[str] = None,
        refresh: bool = False,
        **filters: Any,
    ) -> List[Form]:
        """Asynchronous version of :meth:`list`."""
        result = await self._list_common(
            True,
            study_key=study_key,
            refresh=refresh,
            **filters,
        )
        return result

    def get(self, study_key: str, form_id: int) -> Form:  # type: ignore[override]
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
        result = self._get_common(False, study_key=study_key, item_id=form_id)
        return result  # type: ignore[return-value]

    async def async_get(self, study_key: str, form_id: int) -> Form:  # type: ignore[override]
        """Asynchronous version of :meth:`get`.

        ``refresh=True`` is also passed to :meth:`async_list` to bypass the
        cache.
        """
        return await self._get_common(True, study_key=study_key, item_id=form_id)
