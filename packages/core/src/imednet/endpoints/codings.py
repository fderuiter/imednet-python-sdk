"""Endpoint for managing codings (medical coding) in a study."""

from imednet.core.endpoint.edc_mixin import EdcAsyncListGetEndpoint, EdcSyncListGetEndpoint
from imednet.core.endpoint.strategies import PopStudyKeyStrategy
from imednet.models.codings import Coding


class CodingsOperationDef:
    """TODO: Add docstring."""
    PATH = "codings"
    MODEL = Coding
    _id_param = "codingId"
    STUDY_KEY_STRATEGY = PopStudyKeyStrategy()


class CodingsEndpoint(CodingsOperationDef, EdcSyncListGetEndpoint[Coding]):  # type: ignore[misc]
    """TODO: Add docstring."""
    pass


class AsyncCodingsEndpoint(CodingsOperationDef, EdcAsyncListGetEndpoint[Coding]):  # type: ignore[misc]
    """TODO: Add docstring."""
    pass
