"""Endpoint for managing studies in the iMedNet system."""

from imednet.core.endpoint.mixins import EdcListGetEndpoint
from imednet.core.endpoint.strategies import OptionalStudyKeyStrategy
from imednet.models.studies import Study


class StudiesEndpoint(EdcListGetEndpoint[Study]):
    """
    API endpoint for interacting with studies in the iMedNet system.

    Provides methods to list available studies and retrieve specific studies.
    """

    PATH = ""
    MODEL = Study
    _id_param = "studyKey"
    _enable_cache = True
    STUDY_KEY_STRATEGY = OptionalStudyKeyStrategy()
