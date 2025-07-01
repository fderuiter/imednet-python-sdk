"""Endpoint for managing subjects in a study."""

from typing import Any, List, Optional

from imednet.core.paginator import AsyncPaginator, Paginator
from imednet.endpoints.paged_endpoint_mixin import PagedEndpointMixin
from imednet.models.subjects import Subject


class SubjectsEndpoint(PagedEndpointMixin):
    """API endpoint for interacting with subjects in an iMedNet study."""

    PATH = "/api/v1/edc/studies"
    MODEL = Subject
    PATH_SUFFIX = "subjects"
    ID_FILTER = "subjectKey"
    INCLUDE_STUDY_IN_FILTER = True

    def list(self, study_key: Optional[str] = None, **filters: Any) -> List[Subject]:
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
        """Get a specific subject by key."""
        result = self._get_impl(self._client, Paginator, subject_key, study_key=study_key)
        return result  # type: ignore[return-value]

    async def async_get(self, study_key: str, subject_key: str) -> Subject:
        """Asynchronous version of :meth:`get`."""
        if self._async_client is None:
            raise RuntimeError("Async client not configured")
        return await self._get_impl(
            self._async_client,
            AsyncPaginator,
            subject_key,
            study_key=study_key,
        )
