"""Endpoint for managing users in a study."""

from typing import Any, Awaitable, Dict, List, Optional, Union

from imednet.core.async_client import AsyncClient
from imednet.core.client import Client
from imednet.core.paginator import AsyncPaginator, Paginator
from imednet.endpoints._mixins import ListGetEndpoint
from imednet.models.users import User


class UsersEndpoint(ListGetEndpoint[User]):
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
        client: Client | AsyncClient,
        paginator_cls: Union[type[Paginator], type[AsyncPaginator]],
        *,
        study_key: Optional[str] = None,
        refresh: bool = False,
        extra_params: Optional[Dict[str, Any]] = None,
        include_inactive: bool = False,
        **filters: Any,
    ) -> List[User] | Awaitable[List[User]]:
        params = extra_params or {}
        params["includeInactive"] = str(include_inactive).lower()

        return super()._list_impl(
            client,
            paginator_cls,
            study_key=study_key,
            refresh=refresh,
            extra_params=params,
            **filters,
        )
