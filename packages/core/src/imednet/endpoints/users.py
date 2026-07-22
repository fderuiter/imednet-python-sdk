"""Endpoint for managing users in a study."""

from imednet.core.endpoint.edc_mixin import EdcAsyncListGetEndpoint, EdcSyncListGetEndpoint
from imednet.core.endpoint.strategies import MappingParamProcessor, PopStudyKeyStrategy
from imednet.models.users import User


class UsersOperationDef:
    """Definition for User operations."""

    PATH = "users"
    MODEL = User
    _id_param = "userId"
    STUDY_KEY_STRATEGY = PopStudyKeyStrategy()
    PARAM_PROCESSOR = MappingParamProcessor(
        mapping={"include_inactive": "includeInactive"},
        defaults={"include_inactive": False},
    )


class UsersEndpoint(UsersOperationDef, EdcSyncListGetEndpoint[User]):  # type: ignore[misc]
    """Synchronous endpoint for managing Users."""


class AsyncUsersEndpoint(UsersOperationDef, EdcAsyncListGetEndpoint[User]):  # type: ignore[misc]
    """Asynchronous endpoint for managing Users."""
