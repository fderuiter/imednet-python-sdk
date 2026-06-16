"""Endpoint for managing codings (medical coding) in a study."""

from imednet.core.endpoint.edc_mixin import EdcAsyncListGetEndpoint, EdcSyncListGetEndpoint
from imednet.core.endpoint.strategies import PopStudyKeyStrategy
from imednet.models.codings import Coding


class CodingsOperationDef:
    PATH = "codings"
    MODEL = Coding
    _id_param = "codingId"
    STUDY_KEY_STRATEGY = PopStudyKeyStrategy()

class CodingsEndpoint(CodingsOperationDef, EdcSyncListGetEndpoint[Coding]): # type: ignore[misc]
    pass

class AsyncCodingsEndpoint(CodingsOperationDef, EdcAsyncListGetEndpoint[Coding]): # type: ignore[misc]
    pass
