"""Endpoint for retrieving record revision history in a study."""

from typing import Any, List, Optional, cast

from imednet.core.paginator import Paginator
from imednet.endpoints.base import BaseEndpoint
from imednet.endpoints.helpers import build_paginator
from imednet.models.record_revisions import RecordRevision


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
        paginator = cast(
            Paginator,
            build_paginator(
                self,
                Paginator,
                "recordRevisions",
                study_key,
                page_size,
                filters,
            ),
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
