"""Endpoint for managing forms (eCRFs) in a study."""

from imednet.core.endpoint.mixins import MetadataListGetEndpoint
from imednet.models.forms import Form


class FormsEndpoint(MetadataListGetEndpoint[Form]):
    """
    API endpoint for interacting with forms (eCRFs) in an iMedNet study.

    Provides methods to list and retrieve individual forms.
    """

    PATH = "forms"
    MODEL = Form
    _id_param = "formId"
    _cache_name = "_forms_cache"
