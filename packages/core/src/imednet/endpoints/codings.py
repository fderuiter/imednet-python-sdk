"""Endpoint for managing codings (medical coding) in a study."""

from imednet.core.endpoint.edc_mixin import ClientT, EdcListGetEndpoint
from imednet.core.endpoint.strategies import PopStudyKeyStrategy
from imednet.models.codings import Coding


class CodingsOperationDef:
    """TODO: Add docstring."""

    PATH = "codings"
    MODEL = Coding
    _id_param = "codingId"
    STUDY_KEY_STRATEGY = PopStudyKeyStrategy()

    pass

    pass


class CodingsEndpoint(CodingsOperationDef, EdcListGetEndpoint[Coding, ClientT]):  # type: ignore[misc]
    """TODO: Add docstring."""

    pass


class AsyncCodingsEndpoint(CodingsEndpoint):  # type: ignore[misc]
    """Legacy backwards-compatible async endpoint."""

    def __init__(self, client, ctx=None):
        """TODO: Add docstring."""
        super().__init__(client, ctx=ctx)
        self._async_client = client
