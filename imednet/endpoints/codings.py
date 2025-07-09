"""Endpoint for managing codings (medical coding) in a study."""

from imednet.core.paginator import AsyncPaginator, Paginator  # noqa: F401
from imednet.endpoints._mixins import ListGetEndpoint
from imednet.models.codings import Coding


class CodingsEndpoint(ListGetEndpoint):
    """
    API endpoint for interacting with codings (medical coding) in an iMedNet study.

    Provides methods to list and retrieve individual codings.
    """

    PATH = "codings"
    MODEL = Coding
    _id_param = "codingId"
    _pop_study_filter = True
    _missing_study_exception = KeyError
