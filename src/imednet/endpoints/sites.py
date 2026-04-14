"""Endpoint for managing sites (study locations) in a study."""

from imednet.core.endpoint.base import GenericListGetEndpoint
from imednet.core.endpoint.edc_mixin import EdcEndpointMixin
from imednet.core.endpoint.mixins import KeyErrorPopStudyKeyMixin
from imednet.models.sites import Site


class SitesEndpoint(
    EdcEndpointMixin,
    KeyErrorPopStudyKeyMixin,
    GenericListGetEndpoint[Site],
):
    """
    API endpoint for interacting with sites (study locations) in an iMedNet study.

    Provides methods to list and retrieve individual sites.
    """

    PATH = "sites"
    MODEL = Site
    _id_param = "siteId"
