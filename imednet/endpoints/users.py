"""Endpoint for managing users in a study."""

from imednet.core.endpoint.mixins import EdcListGetEndpoint
from imednet.core.endpoint.strategies import (
    MappingParamProcessor,
    ParamRule,
    PopStudyKeyStrategy,
)
from imednet.models.users import User


class UsersParamProcessor(MappingParamProcessor):
    """Parameter processor for Users endpoint."""

    rules = [
        ParamRule(
            source="include_inactive",
            target="includeInactive",
            default=False,
            transform=lambda x: str(x).lower(),
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
    STUDY_KEY_STRATEGY = PopStudyKeyStrategy
    PARAM_PROCESSOR_CLS = UsersParamProcessor
