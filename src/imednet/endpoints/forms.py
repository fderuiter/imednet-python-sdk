"""Endpoint for managing forms (eCRFs) in a study."""

from imednet.core.endpoint.base import GenericListGetEndpoint
from imednet.core.endpoint.edc_mixin import EdcEndpointMixin
from imednet.core.endpoint.mixins import CachedEndpointMixin, PopStudyKeyMixin
from imednet.models.forms import Form


class FormsEndpoint(
    EdcEndpointMixin,
    CachedEndpointMixin,
    PopStudyKeyMixin,
    GenericListGetEndpoint[Form],
):
    """
    API endpoint for interacting with forms (eCRFs) in an iMedNet study.

    Provides methods to list and retrieve individual forms.
    """

    PATH = "forms"
    MODEL = Form
    _id_param = "formId"
