"""Endpoint for managing variables (data points on eCRFs) in a study."""

from imednet.core.endpoint.edc_mixin import ClientT, EdcListGetEndpoint
from imednet.core.endpoint.strategies import PopStudyKeyStrategy
from imednet.models.variables import Variable


class VariablesOperationDef:
    """TODO: Add docstring."""

    PATH = "variables"
    MODEL = Variable
    _id_param = "variableId"
    STUDY_KEY_STRATEGY = PopStudyKeyStrategy()
    PAGE_SIZE = 500

    pass

    pass


class VariablesEndpoint(VariablesOperationDef, EdcListGetEndpoint[Variable, ClientT]):  # type: ignore[misc]
    """TODO: Add docstring."""

    pass


class AsyncVariablesEndpoint(VariablesEndpoint):  # type: ignore[misc]
    """Legacy backwards-compatible async endpoint."""

    def __init__(self, client, ctx=None):
        """TODO: Add docstring."""
        super().__init__(client, ctx=ctx)
        self._async_client = client
