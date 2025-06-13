"""Endpoint for retrieving record revision history in a study."""

from typing import Any, Dict, List, Optional

from imednet.core.paginator import AsyncPaginator, Paginator
from imednet.endpoints.base import BaseEndpoint
from imednet.models.record_revisions import RecordRevision
from imednet.utils.filters import build_filter_string


class RecordRevisionsEndpoint(BaseEndpoint):
    """
    API endpoint for accessing record revision history in an iMedNet study.

    Provides methods to list and retrieve record revisions.
    """

    PATH = "/api/v1/edc/studies"

    def list(self, study_key: Optional[str] = None, **filters) -> List[RecordRevision]:
        """
        List record revisions in a study with optional filtering.

        Args:
            study_key: Study identifier (uses default from context if not specified)
            **filters: Additional filter parameters

        Returns:
            List of RecordRevision objects
        """
        filters = self._auto_filter(filters)
        if study_key:
            filters["studyKey"] = study_key

        params: Dict[str, Any] = {}
        if filters:
            params["filter"] = build_filter_string(filters)

        path = self._build_path(filters.get("studyKey", ""), "recordRevisions")
        paginator = Paginator(self._client, path, params=params)
        return [RecordRevision.from_json(item) for item in paginator]

    async def async_list(
        self, study_key: Optional[str] = None, **filters: Any
    ) -> List[RecordRevision]:
        """Asynchronous version of :meth:`list`."""
        if self._async_client is None:
            raise RuntimeError("Async client not configured")
        filters = self._auto_filter(filters)
        if study_key:
            filters["studyKey"] = study_key

        params: Dict[str, Any] = {}
        if filters:
            params["filter"] = build_filter_string(filters)

        path = self._build_path(filters.get("studyKey", ""), "recordRevisions")
        paginator = AsyncPaginator(self._async_client, path, params=params)
        return [RecordRevision.from_json(item) async for item in paginator]

    def get(self, study_key: str, record_revision_id: int) -> RecordRevision:
        """
        Get a specific record revision by ID.

        Args:
            study_key: Study identifier
            record_revision_id: Record revision identifier

        Returns:
            RecordRevision object
        """
        revisions = self.list(study_key=study_key, recordRevisionId=record_revision_id)
        if not revisions:
            raise ValueError(f"Record revision {record_revision_id} not found in study {study_key}")
        return revisions[0]

    async def async_get(self, study_key: str, record_revision_id: int) -> RecordRevision:
        """Asynchronous version of :meth:`get`."""
        if self._async_client is None:
            raise RuntimeError("Async client not configured")
        revisions = await self.async_list(study_key=study_key, recordRevisionId=record_revision_id)
        if not revisions:
            raise ValueError(f"Record revision {record_revision_id} not found in study {study_key}")
        return revisions[0]
