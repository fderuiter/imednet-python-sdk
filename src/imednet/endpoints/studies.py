"""Endpoint for managing studies in the iMedNet system."""

from imednet.core.endpoint.base import GenericListGetEndpoint
from imednet.core.endpoint.edc_mixin import EdcEndpointMixin
from imednet.models.studies import Study


class StudiesEndpoint(
    EdcEndpointMixin,
    GenericListGetEndpoint[Study],
):
    """
    API endpoint for interacting with studies in the iMedNet system.

    Provides methods to list available studies and retrieve specific studies.
    """

    PATH = ""
    MODEL = Study
    _id_param = "studyKey"
    _enable_cache = True
    requires_study_key = False
