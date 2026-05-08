"""Endpoint for managing variables (data points on eCRFs) in a study."""

from imednet.core.endpoint.base import GenericListGetEndpoint
from imednet.core.endpoint.cache_mixin import CachedEndpointMixin
from imednet.core.endpoint.edc_mixin import EdcEndpointMixin
from imednet.core.endpoint.strategies import PopStudyKeyStrategy
from imednet.models.variables import Variable


class VariablesEndpoint(
    CachedEndpointMixin[Variable],
    EdcEndpointMixin,
    GenericListGetEndpoint[Variable],
):
    """
    API endpoint for interacting with variables (data points on eCRFs) in an iMedNet study.

    Provides methods to list and retrieve individual variables.
    """

    PATH = "variables"
    MODEL = Variable
    _id_param = "variableId"
    STUDY_KEY_STRATEGY = PopStudyKeyStrategy()
    _enable_cache = True
    PAGE_SIZE = 500
