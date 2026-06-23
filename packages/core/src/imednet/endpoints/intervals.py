"""Endpoint for managing intervals (visit definitions) in a study."""

from imednet.core.endpoint.edc_mixin import ClientT, EdcListGetEndpoint
from imednet.core.endpoint.strategies import PopStudyKeyStrategy
from imednet.models.intervals import Interval


class IntervalsOperationDef:
    """TODO: Add docstring."""

    PATH = "intervals"
    MODEL = Interval
    _id_param = "intervalId"
    STUDY_KEY_STRATEGY = PopStudyKeyStrategy()
    PAGE_SIZE = 500

    pass

    pass


class IntervalsEndpoint(IntervalsOperationDef, EdcListGetEndpoint[Interval, ClientT]):  # type: ignore[misc]
    """TODO: Add docstring."""

    pass


class AsyncIntervalsEndpoint(IntervalsEndpoint):  # type: ignore[misc]
    """Legacy backwards-compatible async endpoint."""

    def __init__(self, client, ctx=None):
        """TODO: Add docstring."""
        super().__init__(client, ctx=ctx)
        self._async_client = client
