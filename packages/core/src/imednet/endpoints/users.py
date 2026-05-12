"""Endpoint for managing users in a study."""

from imednet.core.endpoint.edc_mixin import EdcGenericListGetEndpoint
from imednet.core.endpoint.strategies import MappingParamProcessor, PopStudyKeyStrategy
from imednet.models.users import User


class UsersEndpoint(EdcGenericListGetEndpoint[User]):
    """
    API endpoint for interacting with users in an iMedNet study.

    Provides methods to list and retrieve user information.
    """

    PATH = "users"
    MODEL = User
    _id_param = "userId"
    STUDY_KEY_STRATEGY = PopStudyKeyStrategy()
    PARAM_PROCESSOR = MappingParamProcessor(
        mapping={"include_inactive": "includeInactive"},
        defaults={"include_inactive": False},
    )
