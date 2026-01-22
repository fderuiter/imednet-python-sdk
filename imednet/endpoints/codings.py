"""Endpoint for managing codings (medical coding) in a study."""

from imednet.endpoints._mixins import StudyScopedEndpoint
from imednet.models.codings import Coding


class CodingsEndpoint(StudyScopedEndpoint[Coding]):
    """
    API endpoint for interacting with codings (medical coding) in an iMedNet study.

    Provides methods to list and retrieve individual codings.
    """

    PATH = "codings"
    MODEL = Coding
    _id_param = "codingId"
