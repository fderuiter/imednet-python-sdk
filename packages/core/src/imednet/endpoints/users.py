"""Endpoint for managing users in a study."""

from imednet.core.endpoint.edc_mixin import ClientT, EdcListGetEndpoint
from imednet.core.endpoint.strategies import MappingParamProcessor, PopStudyKeyStrategy
from imednet.models.users import User


class UsersOperationDef:
    """TODO: Add docstring."""

    PATH = "users"
    MODEL = User
    _id_param = "userId"
    STUDY_KEY_STRATEGY = PopStudyKeyStrategy()
    PARAM_PROCESSOR = MappingParamProcessor(
        mapping={"include_inactive": "includeInactive"},
        defaults={"include_inactive": False},
    )




    pass




    pass

class UsersEndpoint(UsersOperationDef, EdcListGetEndpoint[User, ClientT]):  # type: ignore[misc]
    """TODO: Add docstring."""

    pass

class AsyncUsersEndpoint(UsersEndpoint):  # type: ignore[misc]
    """Legacy backwards-compatible async endpoint."""
    def __init__(self, client, ctx=None):
        """TODO: Add docstring."""
        super().__init__(client, ctx=ctx)
        self._async_client = client
