"""Endpoint for managing codings (medical coding) in a study."""

from imednet.core.endpoint.mixins import StrictListGetEndpoint
from imednet.models.codings import Coding


class CodingsEndpoint(StrictListGetEndpoint[Coding]):
    """
    API endpoint for interacting with codings (medical coding) in an iMedNet study.

    Provides methods to list and retrieve individual codings.
    """

    PATH = "codings"
    MODEL = Coding
    _id_param = "codingId"
