"""Endpoint for managing users in a study."""

from typing import Any, List, Optional, Union

from imednet.core.paginator import Paginator  # noqa: F401
from imednet.endpoints.async_endpoint_mixin import AsyncEndpointMixin
from imednet.endpoints.paged_endpoint_mixin import PagedEndpointMixin
from imednet.endpoints.sync_endpoint_mixin import SyncEndpointMixin
from imednet.models.users import User


class UsersEndpoint(SyncEndpointMixin, AsyncEndpointMixin, PagedEndpointMixin):
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
        return super().list(study_key=study_key, **filters)

    async def async_list(
        self,
        study_key: Optional[str] = None,
        include_inactive: bool = False,
        **filters: Any,
    ) -> List[User]:
        """Asynchronous version of :meth:`list`."""
        if include_inactive:
            filters["include_inactive"] = include_inactive
        return await super().async_list(study_key=study_key, **filters)

    def get(self, study_key: str, user_id: Union[str, int]) -> User:  # type: ignore[override]
        """Get a specific user by ID."""
        return super().get(user_id, study_key=study_key)

    async def async_get(self, study_key: str, user_id: Union[str, int]) -> User:  # type: ignore[override]
        """Asynchronous version of :meth:`get`."""
        return await super().async_get(user_id, study_key=study_key)
