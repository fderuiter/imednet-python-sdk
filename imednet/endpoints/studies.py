"""Endpoint for managing studies in the iMedNet system."""

from imednet.core.paginator import AsyncPaginator, Paginator  # noqa: F401
from imednet.endpoints._mixins import ListGetEndpoint
from imednet.models.studies import Study


class StudiesEndpoint(ListGetEndpoint):
    """
    API endpoint for interacting with studies in the iMedNet system.

    Provides methods to list available studies and retrieve specific studies.
    """

    PATH = ""
    MODEL = Study
    _id_param = "studyKey"
    _cache_name = "_studies_cache"
    requires_study_key = False
