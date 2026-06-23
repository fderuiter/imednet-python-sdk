"""Endpoint for managing sites (study locations) in a study."""

from imednet.core.endpoint.edc_mixin import ClientT, EdcListGetEndpoint
from imednet.core.endpoint.strategies import PopStudyKeyStrategy
from imednet.models.sites import Site


class SitesOperationDef:
    """TODO: Add docstring."""

    PATH = "sites"
    MODEL = Site
    _id_param = "siteId"
    STUDY_KEY_STRATEGY = PopStudyKeyStrategy()




    pass




    pass

class SitesEndpoint(SitesOperationDef, EdcListGetEndpoint[Site, ClientT]):  # type: ignore[misc]
    """TODO: Add docstring."""

    pass

class AsyncSitesEndpoint(SitesEndpoint):  # type: ignore[misc]
    """Legacy backwards-compatible async endpoint."""
    def __init__(self, client, ctx=None):
        """TODO: Add docstring."""
        super().__init__(client, ctx=ctx)
        self._async_client = client
