"""Endpoint for managing users in a study."""

from typing import Any, List, Optional, Union

from imednet.core.paginator import AsyncPaginator, Paginator
from imednet.endpoints.base import BaseEndpoint
from imednet.models.users import User
from imednet.utils.filters import build_filter_string as _build_filter_string

from ._mixins import ListGetEndpointMixin

# expose for patching in tests
build_filter_string = _build_filter_string


class UsersEndpoint(ListGetEndpointMixin, BaseEndpoint):
    """
    API endpoint for interacting with users in an iMedNet study.

    Provides methods to list and retrieve user information.
    """

    PATH = "users"
    MODEL = User
    ID_FIELD = "userId"
    _param_map = {"include_inactive": "includeInactive"}
    _requires_study_key = True

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
        result = self._get_impl(
            self._client,
            Paginator,
            study_key=study_key,
            item_id=user_id,
        )
        return result  # type: ignore[return-value]

    async def async_get(self, study_key: str, user_id: Union[str, int]) -> User:
        """Asynchronous version of :meth:`get`."""
        if self._async_client is None:
            raise RuntimeError("Async client not configured")
        return await self._get_impl(
            self._async_client,
            AsyncPaginator,
            study_key=study_key,
            item_id=user_id,
        )
