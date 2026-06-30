"""Endpoint for managing visits (interval instances) in a study."""

from imednet.core.endpoint.edc_mixin import EdcAsyncListGetEndpoint, EdcSyncListGetEndpoint
from imednet.models.visits import Visit


class VisitsOperationDef:
    """Definition for Visit operations."""

    PATH = "visits"
    MODEL = Visit
    _id_param = "visitId"


class VisitsMixin(VisitsOperationDef):
    """Mixin for Visits operations."""

class VisitsEndpoint(VisitsMixin, EdcSyncListGetEndpoint[Visit]):  # type: ignore[misc]
    """Synchronous endpoint for managing Visits."""

    pass


class AsyncVisitsEndpoint(VisitsMixin, EdcAsyncListGetEndpoint[Visit]):  # type: ignore[misc]
    """Asynchronous endpoint for managing Visits."""

    pass
