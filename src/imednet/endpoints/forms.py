"""Endpoint for managing forms (eCRFs) in a study."""

from imednet.core.endpoint.edc_mixin import EdcGenericListGetEndpoint
from imednet.core.endpoint.strategies import PopStudyKeyStrategy
from imednet.models.forms import Form


class FormsEndpoint(EdcGenericListGetEndpoint[Form]):
    """
    API endpoint for interacting with forms (eCRFs) in an iMedNet study.

    Provides methods to list and retrieve individual forms.
    """

    PATH = "forms"
    MODEL = Form
    _id_param = "formId"
    STUDY_KEY_STRATEGY = PopStudyKeyStrategy()
    _enable_cache = True
    PAGE_SIZE = 500
