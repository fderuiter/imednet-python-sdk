"""Endpoint for managing users in a study."""

from typing import Any, Dict, Tuple

from imednet.core.endpoint.mixins import EdcListGetEndpoint
from imednet.core.protocols import ParamProcessor
from imednet.models.users import User


class UsersParamProcessor(ParamProcessor):
    """Parameter processor for Users endpoint."""

    def process_filters(self, filters: Dict[str, Any]) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """
        Extract 'include_inactive' parameter.

        Args:
            filters: The filters dictionary.

        Returns:
            Tuple of (cleaned filters, special parameters).
        """
        filters = filters.copy()
        include_inactive = filters.pop("include_inactive", False)
        special_params = {"includeInactive": str(include_inactive).lower()}
        return filters, special_params


class UsersEndpoint(EdcListGetEndpoint[User]):
    """
    API endpoint for interacting with users in an iMedNet study.

    Provides methods to list and retrieve user information.
    """

    PATH = "users"
    MODEL = User
    _id_param = "userId"
    _pop_study_filter = True
    PARAM_PROCESSOR_CLS = UsersParamProcessor
