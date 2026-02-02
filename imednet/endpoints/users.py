"""Endpoint for managing users in a study."""

from typing import Any, Dict

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

    def _extract_special_params(self, filters: Dict[str, Any]) -> Dict[str, Any]:
        params = {}
        if "include_inactive" in filters:
            val = filters.pop("include_inactive")
            params["includeInactive"] = str(val).lower()
        return params
