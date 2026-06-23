"""Endpoint for managing forms (eCRFs) in a study."""

from imednet.core.endpoint.edc_mixin import ClientT, EdcListGetEndpoint
from imednet.core.endpoint.strategies import PopStudyKeyStrategy
from imednet.models.forms import Form


class FormsOperationDef:
    """TODO: Add docstring."""

    PATH = "forms"
    MODEL = Form
    _id_param = "formId"
    STUDY_KEY_STRATEGY = PopStudyKeyStrategy()
    PAGE_SIZE = 500

    pass

    pass


class FormsEndpoint(FormsOperationDef, EdcListGetEndpoint[Form, ClientT]):  # type: ignore[misc]
    """TODO: Add docstring."""

    pass


class AsyncFormsEndpoint(FormsEndpoint):  # type: ignore[misc]
    """Legacy backwards-compatible async endpoint."""

    def __init__(self, client, ctx=None):
        """TODO: Add docstring."""
        super().__init__(client, ctx=ctx)
        self._async_client = client
