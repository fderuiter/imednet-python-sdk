"""Endpoint for managing forms (eCRFs) in a study."""

from imednet.core.endpoint.base import GenericEndpoint
from imednet.core.endpoint.edc_mixin import EdcEndpointMixin
from imednet.core.endpoint.mixins import FilterGetEndpointMixin, ListEndpointMixin
from imednet.core.endpoint.strategies import PopStudyKeyStrategy
from imednet.models.forms import Form


class FormsEndpoint(
    EdcEndpointMixin,
    GenericEndpoint[Form],
    ListEndpointMixin[Form],
    FilterGetEndpointMixin[Form],
):
    """
    API endpoint for interacting with forms (eCRFs) in an iMedNet study.

    Provides methods to list and retrieve individual forms.
    """

    PATH = "forms"
    MODEL = Form
    _id_param = "formId"
    _enable_cache = True
    STUDY_KEY_STRATEGY = PopStudyKeyStrategy(exception_cls=KeyError)
    PAGE_SIZE = 500
