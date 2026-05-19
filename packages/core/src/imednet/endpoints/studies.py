"""Endpoint for managing studies in the iMedNet system."""

from imednet.core.endpoint.edc_mixin import EdcAsyncListGetEndpoint, EdcSyncListGetEndpoint
from imednet.models.studies import Study


class StudiesEndpoint(EdcSyncListGetEndpoint[Study]):
    """
    API endpoint for interacting with studies in the iMedNet system.

    Provides methods to list available studies and retrieve specific studies.
    """

    PATH = ""
    MODEL = Study
    _id_param = "studyKey"
    requires_study_key: bool = False


class AsyncStudiesEndpoint(EdcAsyncListGetEndpoint[Study]):
    PATH = ""
    MODEL = Study
    _id_param = "studyKey"
    requires_study_key: bool = False
