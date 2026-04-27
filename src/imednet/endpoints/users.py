"""Endpoint for managing users in a study."""

from imednet.core.endpoint.base import GenericListGetEndpoint
from imednet.core.endpoint.edc_mixin import EdcEndpointMixin
from imednet.core.endpoint.mixins import PopStudyKeyMixin
from imednet.core.endpoint.strategies import MappingParamProcessor
from imednet.models.users import User


class UsersEndpoint(
    EdcEndpointMixin,
    PopStudyKeyMixin,
    GenericListGetEndpoint[User],
):
    """
    API endpoint for interacting with users in an iMedNet study.

    Provides methods to list and retrieve user information.
    """

    PATH = "users"
    MODEL = User
    _id_param = "userId"
    PARAM_PROCESSOR = MappingParamProcessor(
        mapping={"include_inactive": "includeInactive"},
        defaults={"include_inactive": False},
    )
