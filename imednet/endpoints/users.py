"""Endpoint for managing users in a study."""

from typing import Any, Dict, Optional

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

    def _prepare_list_params(
        self,
        study_key: Optional[str],
        refresh: bool,
        extra_params: Optional[Dict[str, Any]],
        filters: Dict[str, Any],
    ) -> tuple[Optional[str], Any, Dict[str, Any], Dict[str, Any]]:
        include_inactive = filters.pop("include_inactive", False)

        extra_params = extra_params or {}
        extra_params["includeInactive"] = str(include_inactive).lower()

        return super()._prepare_list_params(study_key, refresh, extra_params, filters)
