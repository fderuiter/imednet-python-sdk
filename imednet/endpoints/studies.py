"""Endpoint for managing studies in the iMedNet system."""

from typing import Any, List

from imednet.core.async_client import AsyncClient
from imednet.core.client import Client
from imednet.core.context import Context
from imednet.core.paginator import AsyncPaginator, Paginator
from imednet.endpoints.paged_endpoint_mixin import PagedEndpointMixin
from imednet.models.studies import Study


class StudiesEndpoint(PagedEndpointMixin):
    """API endpoint for interacting with studies in the iMedNet system."""

    PATH = "/api/v1/edc/studies"
    MODEL = Study
    ID_FILTER = "studyKey"
    CACHE_ENABLED = True

    def __init__(
        self,
        client: Client,
        ctx: Context,
        async_client: AsyncClient | None = None,
    ) -> None:
        super().__init__(client, ctx, async_client)

    def list(self, refresh: bool = False, **filters: Any) -> List[Study]:
        """List studies with optional filtering."""
        result = self._list_impl(
            self._client,
            Paginator,
            refresh=refresh,
            **filters,
        )
        return result  # type: ignore[return-value]

    async def async_list(self, refresh: bool = False, **filters: Any) -> List[Study]:
        """Asynchronous version of :meth:`list`."""
        if self._async_client is None:
            raise RuntimeError("Async client not configured")
        result = await self._list_impl(
            self._async_client,
            AsyncPaginator,
            refresh=refresh,
            **filters,
        )
        return result

    def get(self, study_key: str) -> Study:
        """Get a specific study by key."""
        result = self._get_impl(self._client, Paginator, study_key)
        return result  # type: ignore[return-value]

    async def async_get(self, study_key: str) -> Study:
        """Asynchronous version of :meth:`get`."""
        if self._async_client is None:
            raise RuntimeError("Async client not configured")
        return await self._get_impl(self._async_client, AsyncPaginator, study_key)
