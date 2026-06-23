"""Endpoint for managing studies in the iMedNet system."""

from imednet.core.endpoint.edc_mixin import ClientT, EdcListGetEndpoint
from imednet.models.studies import Study


class StudiesOperationDef:
    """TODO: Add docstring."""

    PATH = ""
    MODEL = Study
    _id_param = "studyKey"
    requires_study_key: bool = False




    pass




    pass

class StudiesEndpoint(StudiesOperationDef, EdcListGetEndpoint[Study, ClientT]):  # type: ignore[misc]
    """TODO: Add docstring."""

    pass

class AsyncStudiesEndpoint(StudiesEndpoint):  # type: ignore[misc]
    """Legacy backwards-compatible async endpoint."""
    def __init__(self, client, ctx=None):
        """TODO: Add docstring."""
        super().__init__(client, ctx=ctx)
        self._async_client = client
