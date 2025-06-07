"""Endpoint for managing subjects in a study."""

from typing import Any, List, Optional, cast

from imednet.core.paginator import Paginator
from imednet.endpoints.base import BaseEndpoint
from imednet.endpoints.helpers import build_paginator
from imednet.models.subjects import Subject


class SubjectsEndpoint(BaseEndpoint):
    """
    API endpoint for interacting with subjects in an iMedNet study.

    Provides methods to list and retrieve individual subjects.
    """

    path = "/api/v1/edc/studies"

    def list(
        self,
        study_key: Optional[str] = None,
        page_size: Optional[int] = None,
        **filters: Any,
    ) -> List[Subject]:
        """
        List subjects in a study with optional filtering.

        Args:
            study_key: Study identifier (uses default from context if not specified)
            ``**filters``: Additional filter parameters

        Returns:
            List of Subject objects
        """
        paginator = cast(
            Paginator,
            build_paginator(
                self,
                Paginator,
                "subjects",
                study_key,
                page_size,
                filters,
            ),
        )
        return [Subject.from_json(item) for item in paginator]

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
