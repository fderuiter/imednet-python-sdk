"""Endpoint for managing forms (eCRFs) in a study."""

from imednet.core.paginator import AsyncPaginator, Paginator  # noqa: F401
from imednet.endpoints._mixins import ListGetEndpoint
from imednet.models.forms import Form


class FormsEndpoint(ListGetEndpoint):
    """
    API endpoint for interacting with forms (eCRFs) in an iMedNet study.

    Provides methods to list and retrieve individual forms.
    """

    PATH = "forms"
    MODEL = Form
    _id_param = "formId"
    _cache_name = "_forms_cache"
    PAGE_SIZE = 500
    _pop_study_filter = True
    _missing_study_exception = KeyError
