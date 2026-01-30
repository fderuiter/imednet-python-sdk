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
        include_inactive = filters.pop("include_inactive", False)
        return {"includeInactive": str(include_inactive).lower()}
