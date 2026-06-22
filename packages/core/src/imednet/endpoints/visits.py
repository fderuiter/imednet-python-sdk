"""Endpoint for managing visits (interval instances) in a study."""

from imednet.core.endpoint.edc_mixin import EdcAsyncListGetEndpoint, EdcSyncListGetEndpoint
from imednet.models.visits import Visit


class VisitsOperationDef:
    """TODO: Add docstring."""

    PATH = "visits"
    MODEL = Visit
    _id_param = "visitId"


class VisitsEndpoint(VisitsOperationDef, EdcSyncListGetEndpoint[Visit]):  # type: ignore[misc]
    """TODO: Add docstring."""

    pass


class AsyncVisitsEndpoint(VisitsOperationDef, EdcAsyncListGetEndpoint[Visit]):  # type: ignore[misc]
    """TODO: Add docstring."""

    pass
