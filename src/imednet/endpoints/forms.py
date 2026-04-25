"""Endpoint for managing forms (eCRFs) in a study."""

from imednet.core.endpoint.base import GenericListGetEndpoint
from imednet.core.endpoint.edc_mixin import EdcEndpointMixin
from imednet.core.endpoint.mixins import CachedEndpointMixin
from imednet.core.endpoint.mixins.params import PopStudyKeyMixin
from imednet.models.forms import Form


class FormsEndpoint(
    EdcEndpointMixin,
    PopStudyKeyMixin,
    CachedEndpointMixin,
    GenericListGetEndpoint[Form],
):
    """
    API endpoint for interacting with forms (eCRFs) in an iMedNet study.

    Provides methods to list and retrieve individual forms.
    """

    PATH = "forms"
    MODEL = Form
    _id_param = "formId"
