"""Endpoint for managing subjects in a study."""

from imednet.core.paginator import AsyncPaginator, Paginator  # noqa: F401
from imednet.endpoints._mixins import ListGetEndpoint
from imednet.models.subjects import Subject


class SubjectsEndpoint(ListGetEndpoint):
    """
    API endpoint for interacting with subjects in an iMedNet study.

    Provides methods to list and retrieve individual subjects.
    """

    PATH = "subjects"
    MODEL = Subject
    _id_param = "subjectKey"
