"""Endpoint for managing variables (data points on eCRFs) in a study."""

from ..core.paginator import AsyncPaginator, Paginator  # noqa: F401
from ..models.variables import Variable
from ._mixins import ListGetEndpoint
from .registry import register_endpoint


@register_endpoint("variables")
class VariablesEndpoint(ListGetEndpoint):
    """
    API endpoint for interacting with variables (data points on eCRFs) in an iMedNet study.

    Provides methods to list and retrieve individual variables.
    """

    PATH = "variables"
    MODEL = Variable
    _id_param = "variableId"
    _cache_name = "_variables_cache"
    PAGE_SIZE = 500
    _pop_study_filter = True
    _missing_study_exception = KeyError
