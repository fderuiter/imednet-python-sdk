"""Endpoint for retrieving record revision history in a study."""

from typing import Any, Dict, List, Optional

from imednet.core.paginator import Paginator
from imednet.endpoints.base import BaseEndpoint
from imednet.models.record_revisions import RecordRevision
from imednet.utils.filters import build_filter_string


class RecordRevisionsEndpoint(BaseEndpoint):
    """
    API endpoint for accessing record revision history in an iMedNet study.

    Provides methods to list and retrieve record revisions.
    """

    path = "/api/v1/edc/studies"

    def list(
        self,
        study_key: Optional[str] = None,
        page_size: Optional[int] = None,
        **filters: Any,
    ) -> List[RecordRevision]:
        """
        List record revisions in a study with optional filtering.

        Args:
            study_key: Study identifier (uses default from context if not specified)
            ``**filters``: Additional filter parameters

        Returns:
            List of RecordRevision objects
        """
        filters = self._auto_filter(filters)
        if study_key:
            filters["studyKey"] = study_key

        params: Dict[str, Any] = {}
        filter_arg = filters.pop("filter", None)
        if filter_arg:
            params["filter"] = (
                filter_arg if isinstance(filter_arg, str) else build_filter_string(filter_arg)
            )
        elif filters:
            params["filter"] = build_filter_string(filters)

        path = self._build_path(filters.get("studyKey", ""), "recordRevisions")
        paginator = Paginator(
            self._client,
            path,
            params=params,
            page_size=page_size or self._default_page_size,
        )
        return [RecordRevision.from_json(item) for item in paginator]

    def get(self, study_key: str, record_revision_id: int) -> RecordRevision:
        """
        Get a specific record revision by ID.

        Args:
            study_key: Study identifier
            record_revision_id: Record revision identifier

        Returns:
            RecordRevision object
        """
        path = self._build_path(study_key, "recordRevisions", record_revision_id)
        raw = self._client.get(path).json().get("data", [])
        if not raw:
            raise ValueError(f"Record revision {record_revision_id} not found in study {study_key}")
        return RecordRevision.from_json(raw[0])
