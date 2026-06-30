"""Endpoint for managing variables (data points on eCRFs) in a study."""

from imednet.core.endpoint.edc_mixin import EdcAsyncListGetEndpoint, EdcSyncListGetEndpoint
from imednet.core.endpoint.strategies import PopStudyKeyStrategy
from imednet.models.variables import Variable


class VariablesOperationDef:
    """Definition for Variable operations."""

    PATH = "variables"
    MODEL = Variable
    _id_param = "variableId"
    STUDY_KEY_STRATEGY = PopStudyKeyStrategy()
    PAGE_SIZE = 500


class VariablesMixin(VariablesOperationDef):
    """Mixin for Variables operations."""

class VariablesEndpoint(VariablesMixin, EdcSyncListGetEndpoint[Variable]):  # type: ignore[misc]
    """Synchronous endpoint for managing Variables."""

    pass


class AsyncVariablesEndpoint(VariablesMixin, EdcAsyncListGetEndpoint[Variable]):  # type: ignore[misc]
    """Asynchronous endpoint for managing Variables."""

    pass
