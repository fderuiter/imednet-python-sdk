"""Endpoint for managing visits (interval instances) in a study."""

from imednet.core.endpoint.edc_mixin import EdcAsyncListGetEndpoint, EdcSyncListGetEndpoint
from imednet.models.visits import Visit


class VisitsEndpoint(EdcSyncListGetEndpoint[Visit]):
    """
    API endpoint for interacting with visits (interval instances) in an iMedNet study.

    Provides methods to list and retrieve individual visits.
    """

    PATH = "visits"
    MODEL = Visit
    _id_param = "visitId"


class AsyncVisitsEndpoint(EdcAsyncListGetEndpoint[Visit]):
    PATH = "visits"
    MODEL = Visit
    _id_param = "visitId"
