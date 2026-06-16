"""Endpoint for managing forms (eCRFs) in a study."""

from imednet.core.endpoint.edc_mixin import EdcAsyncListGetEndpoint, EdcSyncListGetEndpoint
from imednet.core.endpoint.strategies import PopStudyKeyStrategy
from imednet.models.forms import Form


class FormsOperationDef:
    PATH = "forms"
    MODEL = Form
    _id_param = "formId"
    STUDY_KEY_STRATEGY = PopStudyKeyStrategy()
    PAGE_SIZE = 500


class FormsEndpoint(FormsOperationDef, EdcSyncListGetEndpoint[Form]):  # type: ignore[misc]
    pass


class AsyncFormsEndpoint(FormsOperationDef, EdcAsyncListGetEndpoint[Form]):  # type: ignore[misc]
    pass
