"""Endpoint for managing visits (interval instances) in a study."""

from imednet.core.endpoint.edc_mixin import ClientT, EdcListGetEndpoint
from imednet.models.visits import Visit


class VisitsOperationDef:
    """TODO: Add docstring."""

    PATH = "visits"
    MODEL = Visit
    _id_param = "visitId"

    pass

    pass


class VisitsEndpoint(VisitsOperationDef, EdcListGetEndpoint[Visit, ClientT]):  # type: ignore[misc]
    """TODO: Add docstring."""

    pass


class AsyncVisitsEndpoint(VisitsEndpoint):  # type: ignore[misc]
    """Legacy backwards-compatible async endpoint."""

    def __init__(self, client, ctx=None):
        """TODO: Add docstring."""
        super().__init__(client, ctx=ctx)
        self._async_client = client
