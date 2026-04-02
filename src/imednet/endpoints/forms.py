"""Endpoint for managing forms (eCRFs) in a study."""

from imednet.core.endpoint.base import GenericEndpoint
from imednet.core.endpoint.edc_mixin import EdcEndpointMixin
from imednet.core.endpoint.mixins import FilterGetEndpointMixin, ListEndpointMixin
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
    _pop_study_filter = True
    _missing_study_exception = KeyError
    PAGE_SIZE = 500
