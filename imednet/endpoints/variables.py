"""Endpoint for managing variables (data points on eCRFs) in a study."""

from imednet.core.endpoint.mixins import ListGetEndpoint
from imednet.core.endpoint.mixins.edc import EdcEndpointMixin
from imednet.models.variables import Variable


class VariablesEndpoint(EdcEndpointMixin, ListGetEndpoint[Variable]):
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
