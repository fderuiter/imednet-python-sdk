"""Endpoint for managing sites (study locations) in a study."""

from imednet.core.paginator import AsyncPaginator, Paginator  # noqa: F401
from imednet.endpoints._mixins import ListGetEndpoint
from imednet.models.sites import Site


class SitesEndpoint(ListGetEndpoint):
    """
    API endpoint for interacting with sites (study locations) in an iMedNet study.

    Provides methods to list and retrieve individual sites.
    """

    PATH = "sites"
    MODEL = Site
    _id_param = "siteId"
    _pop_study_filter = True
    _missing_study_exception = KeyError
