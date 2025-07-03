"""Endpoint for managing subjects in a study."""

from typing import Any, List, Optional

from imednet.core.paginator import AsyncPaginator, Paginator
from imednet.endpoints._mixins import ListGetEndpointMixin
from imednet.endpoints.base import BaseEndpoint
from imednet.models.subjects import Subject


class SubjectsEndpoint(ListGetEndpointMixin, BaseEndpoint):
    """
    API endpoint for interacting with subjects in an iMedNet study.

    Provides methods to list and retrieve individual subjects.
    """

    PATH = "subjects"
    MODEL = Subject
    _id_param = "subjectKey"

    def list(self, study_key: Optional[str] = None, **filters) -> List[Subject]:
        """List subjects in a study with optional filtering."""
        result = self._list_impl(
            self._client,
            Paginator,
            study_key=study_key,
            **filters,
        )
        return result  # type: ignore[return-value]

    async def async_list(self, study_key: Optional[str] = None, **filters: Any) -> List[Subject]:
        """Asynchronous version of :meth:`list`."""
        if self._async_client is None:
            raise RuntimeError("Async client not configured")
        result = await self._list_impl(
            self._async_client,
            AsyncPaginator,
            study_key=study_key,
            **filters,
        )
        return result

    def get(self, study_key: str, subject_key: str) -> Subject:
        """
        Get a specific subject by key.

        The ``subject_key`` is passed as a filter to :meth:`list`.

        Args:
            study_key: Study identifier
            subject_key: Subject identifier

        Returns:
            Subject object
        """
        result = self._get_impl(self._client, Paginator, study_key, subject_key)
        return result  # type: ignore[return-value]

    async def async_get(self, study_key: str, subject_key: str) -> Subject:
        """Asynchronous version of :meth:`get`.

        This call also filters :meth:`async_list` by ``subject_key``.
        """
        if self._async_client is None:
            raise RuntimeError("Async client not configured")
        return await self._get_impl(
            self._async_client,
            AsyncPaginator,
            study_key,
            subject_key,
        )
