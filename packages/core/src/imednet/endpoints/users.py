"""Endpoint for managing users in a study."""

from imednet.core.endpoint.edc_mixin import EdcAsyncListGetEndpoint, EdcSyncListGetEndpoint
from imednet.core.endpoint.strategies import MappingParamProcessor, PopStudyKeyStrategy
from imednet.models.users import User

class UsersOperationDef:
    PATH = "users"
    MODEL = User
    _id_param = "userId"
    STUDY_KEY_STRATEGY = PopStudyKeyStrategy()
    PARAM_PROCESSOR = MappingParamProcessor(
    mapping={"include_inactive": "includeInactive"},
    defaults={"include_inactive": False},
    )

class UsersEndpoint(UsersOperationDef, EdcSyncListGetEndpoint[User]): # type: ignore[misc]
    pass

class AsyncUsersEndpoint(UsersOperationDef, EdcAsyncListGetEndpoint[User]): # type: ignore[misc]
    pass
