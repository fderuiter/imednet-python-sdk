"""Endpoint for managing sites (study locations) in a study."""

from imednet.core.endpoint.mixins import ListGetEndpoint
from imednet.core.endpoint.mixins.edc import EdcEndpointMixin
from imednet.models.sites import Site


class SitesEndpoint(EdcEndpointMixin, ListGetEndpoint[Site]):
    """
    API endpoint for interacting with sites (study locations) in an iMedNet study.

    Provides methods to list and retrieve individual sites.
    """

    PATH = "sites"
    MODEL = Site
    _id_param = "siteId"
    _pop_study_filter = True
    _missing_study_exception = KeyError
