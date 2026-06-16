"""Endpoint for managing variables (data points on eCRFs) in a study."""

from imednet.core.endpoint.edc_mixin import EdcAsyncListGetEndpoint, EdcSyncListGetEndpoint
from imednet.core.endpoint.strategies import PopStudyKeyStrategy
from imednet.models.variables import Variable


class VariablesOperationDef:
    PATH = "variables"
    MODEL = Variable
    _id_param = "variableId"
    STUDY_KEY_STRATEGY = PopStudyKeyStrategy()
    PAGE_SIZE = 500

class VariablesEndpoint(VariablesOperationDef, EdcSyncListGetEndpoint[Variable]): # type: ignore[misc]
    pass

class AsyncVariablesEndpoint(VariablesOperationDef, EdcAsyncListGetEndpoint[Variable]): # type: ignore[misc]
    pass
