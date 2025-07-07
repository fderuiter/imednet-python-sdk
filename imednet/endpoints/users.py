"""Endpoint for managing users in a study."""

from typing import Any, List, Optional, Union

from imednet.core.paginator import AsyncPaginator, Paginator
from imednet.endpoints._mixins import ListGetEndpointMixin
from imednet.endpoints.base import BaseEndpoint
from imednet.models.users import User


class UsersEndpoint(ListGetEndpointMixin, BaseEndpoint):
    """
    API endpoint for interacting with users in an iMedNet study.

    Provides methods to list and retrieve user information.
    """

    PATH = "users"
    MODEL = User
    _id_param = "userId"
    _pop_study_filter = True

    def _list_impl(
        self,
        client: Any,
        paginator_cls: type[Any],
        *,
        study_key: Optional[str] = None,
        include_inactive: bool = False,
        **filters: Any,
    ) -> Any:
        params = {"includeInactive": str(include_inactive).lower()}
        return super()._list_impl(
            client,
            paginator_cls,
            study_key=study_key,
            extra_params=params,
            **filters,
        )

    def list(
        self, study_key: Optional[str] = None, include_inactive: bool = False, **filters: Any
    ) -> List[User]:
        """List users in a study with optional filtering."""
        result = self._list_impl(
            self._client,
            Paginator,
            study_key=study_key,
            include_inactive=include_inactive,
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
        result = await self._list_impl(
            self._async_client,
            AsyncPaginator,
            study_key=study_key,
            include_inactive=include_inactive,
            **filters,
        )
        return result

    def get(self, study_key: str, user_id: Union[str, int]) -> User:
        """
        Get a specific user by ID.

        Args:
            study_key: Study identifier
            user_id: User identifier (can be a string UUID or integer ID)

        Returns:
            User object
        """
        result = self._get_impl(self._client, Paginator, study_key=study_key, item_id=user_id)
        return result  # type: ignore[return-value]

    async def async_get(self, study_key: str, user_id: Union[str, int]) -> User:
        """Asynchronous version of :meth:`get`."""
        if self._async_client is None:
            raise RuntimeError("Async client not configured")
        return await self._get_impl(
            self._async_client, AsyncPaginator, study_key=study_key, item_id=user_id
        )
