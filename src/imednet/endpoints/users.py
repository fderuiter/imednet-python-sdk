"""Endpoint for managing users in a study."""

from imednet.core.endpoint.mixins import EdcListGetEndpoint
from imednet.core.endpoint.strategies import MappingParamProcessor
from imednet.models.users import User


class UsersEndpoint(EdcListGetEndpoint[User]):
    """
    API endpoint for interacting with users in an iMedNet study.

    Provides methods to list and retrieve user information.
    """

    PATH = "users"
    MODEL = User
    _id_param = "userId"
    _pop_study_filter = True
    PARAM_PROCESSOR = MappingParamProcessor(
        mapping={"include_inactive": "includeInactive"},
        defaults={"include_inactive": False},
    )
