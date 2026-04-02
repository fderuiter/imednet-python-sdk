"""Endpoint for managing variables (data points on eCRFs) in a study."""

from imednet.core.endpoint.base import GenericEndpoint
from imednet.core.endpoint.edc_mixin import EdcEndpointMixin
from imednet.core.endpoint.mixins import FilterGetEndpointMixin, ListEndpointMixin
from imednet.models.variables import Variable


class VariablesEndpoint(
    EdcEndpointMixin,
    GenericEndpoint[Variable],
    ListEndpointMixin[Variable],
    FilterGetEndpointMixin[Variable],
):
    """
    API endpoint for interacting with variables (data points on eCRFs) in an iMedNet study.

    Provides methods to list and retrieve individual variables.
    """

    PATH = "variables"
    MODEL = Variable
    _id_param = "variableId"
    _enable_cache = True
    _pop_study_filter = True
    _missing_study_exception = KeyError
    PAGE_SIZE = 500
