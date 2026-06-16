"""Endpoint for managing intervals (visit definitions) in a study."""

from imednet.core.endpoint.edc_mixin import EdcAsyncListGetEndpoint, EdcSyncListGetEndpoint
from imednet.core.endpoint.strategies import PopStudyKeyStrategy
from imednet.models.intervals import Interval


class IntervalsOperationDef:
    PATH = "intervals"
    MODEL = Interval
    _id_param = "intervalId"
    STUDY_KEY_STRATEGY = PopStudyKeyStrategy()
    PAGE_SIZE = 500

class IntervalsEndpoint(IntervalsOperationDef, EdcSyncListGetEndpoint[Interval]): # type: ignore[misc]
    pass

class AsyncIntervalsEndpoint(IntervalsOperationDef, EdcAsyncListGetEndpoint[Interval]): # type: ignore[misc]
    pass
