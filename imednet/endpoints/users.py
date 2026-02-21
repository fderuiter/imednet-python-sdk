"""Endpoint for managing users in a study."""

from imednet.core.endpoint.mixins import EdcListGetEndpoint
from imednet.core.endpoint.strategies import MappingParamProcessor, ParamRule
from imednet.models.users import User


class UsersParamProcessor(MappingParamProcessor):
    """Parameter processor for Users endpoint."""

    rules = [
        ParamRule(
            input_key="include_inactive",
            output_key="includeInactive",
            default=False,
            transform=lambda x: str(x).lower(),
            skip_falsey=False,
        )
    ]


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
