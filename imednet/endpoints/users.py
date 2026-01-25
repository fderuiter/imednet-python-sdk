"""Endpoint for managing users in a study."""

from typing import Any, List, Optional

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

    def list(
        self,
        study_key: Optional[str] = None,
        include_inactive: bool = False,
        **filters: Any,
    ) -> List[User]:
        params = {"includeInactive": str(include_inactive).lower()}
        return super().list(study_key=study_key, extra_params=params, **filters)

    async def async_list(
        self,
        study_key: Optional[str] = None,
        include_inactive: bool = False,
        **filters: Any,
    ) -> List[User]:
        params = {"includeInactive": str(include_inactive).lower()}
        return await super().async_list(study_key=study_key, extra_params=params, **filters)
