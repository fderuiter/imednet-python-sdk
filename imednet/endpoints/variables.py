"""Endpoint for managing variables (data points on eCRFs) in a study."""

from imednet.core.endpoint.mixins import EdcMetadataListGetEndpoint
from imednet.models.variables import Variable


class VariablesEndpoint(EdcMetadataListGetEndpoint[Variable]):
    """
    API endpoint for interacting with variables (data points on eCRFs) in an iMedNet study.

    Provides methods to list and retrieve individual variables.
    """

    PATH = "variables"
    MODEL = Variable
    _id_param = "variableId"
    _cache_name = "_variables_cache"
