"""Endpoint for managing subjects in a study."""

from typing import Any, Dict, List, Optional

from imednet.core.paginator import AsyncPaginator, Paginator
from imednet.endpoints.base import BaseEndpoint
from imednet.models.subjects import Subject
from imednet.utils.filters import build_filter_string


class SubjectsEndpoint(BaseEndpoint):
    """
    API endpoint for interacting with subjects in an iMedNet study.

    Provides methods to list and retrieve individual subjects.
    """

    PATH = "/api/v1/edc/studies"

    def list(self, study_key: Optional[str] = None, **filters) -> List[Subject]:
        """
        List subjects in a study with optional filtering.

        Args:
            study_key: Study identifier (uses default from context if not specified)
            **filters: Additional filter parameters

        Returns:
            List of Subject objects
        """
        filters = self._auto_filter(filters)
        if study_key:
            filters["studyKey"] = study_key

        params: Dict[str, Any] = {}
        if filters:
            params["filter"] = build_filter_string(filters)

        path = self._build_path(filters.get("studyKey", ""), "subjects")
        paginator = Paginator(self._client, path, params=params)
        return [Subject.from_json(item) for item in paginator]

    async def async_list(self, study_key: Optional[str] = None, **filters: Any) -> List[Subject]:
        """Asynchronous version of :meth:`list`."""
        if self._async_client is None:
            raise RuntimeError("Async client not configured")
        filters = self._auto_filter(filters)
        if study_key:
            filters["studyKey"] = study_key

        params: Dict[str, Any] = {}
        if filters:
            params["filter"] = build_filter_string(filters)

        path = self._build_path(filters.get("studyKey", ""), "subjects")
        paginator = AsyncPaginator(self._async_client, path, params=params)
        return [Subject.from_json(item) async for item in paginator]

    def get(self, study_key: str, subject_key: str) -> Subject:
        """
        Get a specific subject by key.

        Args:
            study_key: Study identifier
            subject_key: Subject identifier

        Returns:
            Subject object
        """
        path = self._build_path(study_key, "subjects", subject_key)
        raw = self._client.get(path).json().get("data", [])
        if not raw:
            raise ValueError(f"Subject {subject_key} not found in study {study_key}")
        return Subject.from_json(raw[0])

    async def async_get(self, study_key: str, subject_key: str) -> Subject:
        """Asynchronous version of :meth:`get`."""
        if self._async_client is None:
            raise RuntimeError("Async client not configured")
        path = self._build_path(study_key, "subjects", subject_key)
        raw = (await self._async_client.get(path)).json().get("data", [])
        if not raw:
            raise ValueError(f"Subject {subject_key} not found in study {study_key}")
        return Subject.from_json(raw[0])
