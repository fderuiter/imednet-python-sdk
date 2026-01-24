"""Endpoint for managing users in a study."""

from typing import Any, Optional

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

    def _prepare_request(
        self,
        study_key: Optional[str] = None,
        refresh: bool = False,
        extra_params: Optional[dict[str, Any]] = None,
        include_inactive: bool = False,
        **filters: Any,
    ) -> Any:
        extra_params = extra_params or {}
        extra_params["includeInactive"] = str(include_inactive).lower()
        return super()._prepare_request(
            study_key=study_key,
            refresh=refresh,
            extra_params=extra_params,
            **filters,
        )
