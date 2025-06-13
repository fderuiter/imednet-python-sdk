"""Endpoint for managing codings (medical coding) in a study."""

from typing import Any, Dict, List, Optional

from imednet.core.paginator import AsyncPaginator, Paginator
from imednet.endpoints.base import BaseEndpoint
from imednet.models.codings import Coding
from imednet.utils.filters import build_filter_string


class CodingsEndpoint(BaseEndpoint):
    """
    API endpoint for interacting with codings (medical coding) in an iMedNet study.

    Provides methods to list and retrieve individual codings.
    """

    PATH = "/api/v1/edc/studies"

    def list(self, study_key: Optional[str] = None, **filters) -> List[Coding]:
        """
        List codings in a study with optional filtering.

        Args:
            study_key: Study identifier (uses default from context if not specified)
            filters: Additional filter parameters

        Returns:
            List of Coding objects
        """

        filters = self._auto_filter(filters)
        if study_key:
            filters["studyKey"] = study_key

        study = filters.pop("studyKey")
        if not study:
            raise ValueError("Study key must be provided or set in the context")

        params: Dict[str, Any] = {}
        if filters:
            params["filter"] = build_filter_string(filters)

        path = self._build_path(study, "codings")
        paginator = Paginator(self._client, path, params=params)
        return [Coding.from_json(item) for item in paginator]

    async def async_list(self, study_key: Optional[str] = None, **filters: Any) -> List[Coding]:
        """Asynchronous version of :meth:`list`."""
        if self._async_client is None:
            raise RuntimeError("Async client not configured")
        filters = self._auto_filter(filters)
        if study_key:
            filters["studyKey"] = study_key

        study = filters.pop("studyKey")
        if not study:
            raise ValueError("Study key must be provided or set in the context")

        params: Dict[str, Any] = {}
        if filters:
            params["filter"] = build_filter_string(filters)

        path = self._build_path(study, "codings")
        paginator = AsyncPaginator(self._async_client, path, params=params)
        return [Coding.from_json(item) async for item in paginator]

    def get(self, study_key: str, coding_id: str) -> Coding:
        """
        Get a specific coding by ID.

        Args:
            study_key: Study identifier
            coding_id: Coding identifier

        Returns:
            Coding object
        """

        codings = self.list(study_key=study_key, codingId=coding_id)
        if not codings:
            raise ValueError(f"Coding {coding_id} not found in study {study_key}")
        return codings[0]

    async def async_get(self, study_key: str, coding_id: str) -> Coding:
        """Asynchronous version of :meth:`get`."""
        if self._async_client is None:
            raise RuntimeError("Async client not configured")
        codings = await self.async_list(study_key=study_key, codingId=coding_id)
        if not codings:
            raise ValueError(f"Coding {coding_id} not found in study {study_key}")
        return codings[0]
