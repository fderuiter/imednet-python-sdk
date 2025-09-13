"""Endpoint for managing codings (medical coding) in a study."""

from ..models.codings import Coding
from ._mixins import ListGetEndpoint
from .registry import register_endpoint


@register_endpoint("codings")
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
