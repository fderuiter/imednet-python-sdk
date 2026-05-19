"""Endpoint for managing sites (study locations) in a study."""

from imednet.core.endpoint.edc_mixin import EdcAsyncListGetEndpoint, EdcSyncListGetEndpoint
from imednet.core.endpoint.strategies import PopStudyKeyStrategy
from imednet.models.sites import Site


class SitesEndpoint(EdcSyncListGetEndpoint[Site]):
    """
    API endpoint for interacting with sites (study locations) in an iMedNet study.

    Provides methods to list and retrieve individual sites.
    """

    PATH = "sites"
    MODEL = Site
    _id_param = "siteId"
    STUDY_KEY_STRATEGY = PopStudyKeyStrategy()


class AsyncSitesEndpoint(EdcAsyncListGetEndpoint[Site]):
    PATH = "sites"
    MODEL = Site
    _id_param = "siteId"
    STUDY_KEY_STRATEGY = PopStudyKeyStrategy()
