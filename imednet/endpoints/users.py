"""Endpoint for managing users in a study."""

from typing import Any, List, Optional, Union

from imednet.core.paginator import AsyncPaginator, Paginator
from imednet.endpoints.paged_endpoint_mixin import PagedEndpointMixin
from imednet.models.users import User


class UsersEndpoint(PagedEndpointMixin):
    """API endpoint for interacting with users in an iMedNet study."""

    PATH = "/api/v1/edc/studies"
    MODEL = User
    PATH_SUFFIX = "users"
    ID_FILTER = "userId"
    INCLUDE_STUDY_IN_FILTER = False
    MISSING_STUDY_ERROR = ValueError

    def list(
        self, study_key: Optional[str] = None, include_inactive: bool = False, **filters: Any
    ) -> List[User]:
        """List users in a study with optional filtering."""
        if include_inactive:
            filters["include_inactive"] = include_inactive
        result = self._list_impl(
            self._client,
            Paginator,
            study_key=study_key,
            **filters,
        )
        return result  # type: ignore[return-value]

    async def async_list(
        self,
        study_key: Optional[str] = None,
        include_inactive: bool = False,
        **filters: Any,
    ) -> List[User]:
        """Asynchronous version of :meth:`list`."""
        if self._async_client is None:
            raise RuntimeError("Async client not configured")
        if include_inactive:
            filters["include_inactive"] = include_inactive
        result = await self._list_impl(
            self._async_client,
            AsyncPaginator,
            study_key=study_key,
            **filters,
        )
        return result

    def get(self, study_key: str, user_id: Union[str, int]) -> User:
        """Get a specific user by ID."""
        result = self._get_impl(self._client, Paginator, user_id, study_key=study_key)
        return result  # type: ignore[return-value]

    async def async_get(self, study_key: str, user_id: Union[str, int]) -> User:
        """Asynchronous version of :meth:`get`."""
        if self._async_client is None:
            raise RuntimeError("Async client not configured")
        return await self._get_impl(
            self._async_client, AsyncPaginator, user_id, study_key=study_key
        )
