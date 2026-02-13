"""Endpoint for managing sites (study locations) in a study."""

from imednet.core.endpoint.mixins import StrictListGetEndpoint
from imednet.models.sites import Site


class SitesEndpoint(StrictListGetEndpoint[Site]):
    """
    API endpoint for interacting with sites (study locations) in an iMedNet study.

    Provides methods to list and retrieve individual sites.
    """

    PATH = "sites"
    MODEL = Site
    _id_param = "siteId"
