"""Endpoint for managing subjects in a study."""

from ..core.paginator import AsyncPaginator, Paginator  # noqa: F401
from ..models.subjects import Subject
from ._mixins import ListGetEndpoint
from .registry import register_endpoint


@register_endpoint("subjects")
class SubjectsEndpoint(ListGetEndpoint):
    """
    API endpoint for interacting with subjects in an iMedNet study.

    Provides methods to list and retrieve individual subjects.
    """

    PATH = "subjects"
    MODEL = Subject
    _id_param = "subjectKey"
