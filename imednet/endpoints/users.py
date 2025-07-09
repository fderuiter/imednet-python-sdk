"""Endpoint for managing users in a study."""

from typing import Any, Optional

from imednet.core.paginator import AsyncPaginator, Paginator  # noqa: F401
from imednet.endpoints._mixins import ListGetEndpoint
from imednet.models.users import User


class UsersEndpoint(ListGetEndpoint):
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
