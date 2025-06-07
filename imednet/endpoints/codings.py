"""Endpoint for managing codings (medical coding) in a study."""

from typing import Any, List, Optional, cast

from imednet.core.paginator import Paginator
from imednet.endpoints.base import BaseEndpoint
from imednet.endpoints.helpers import build_paginator
from imednet.models.codings import Coding


class CodingsEndpoint(BaseEndpoint):
    """
    API endpoint for interacting with codings (medical coding) in an iMedNet study.

    Provides methods to list and retrieve individual codings.
    """

    path = "/api/v1/edc/studies"

    def list(
        self,
        study_key: Optional[str] = None,
        page_size: Optional[int] = None,
        **filters: Any,
    ) -> List[Coding]:
        """
        List codings in a study with optional filtering.

        Args:
            study_key: Study identifier (uses default from context if not specified)
            ``**filters``: Additional filter parameters

        Returns:
            List of Coding objects
        """
        paginator = cast(
            Paginator,
            build_paginator(
                self,
                Paginator,
                "codings",
                study_key,
                page_size,
                filters,
            ),
        )
        return [Coding.from_json(item) for item in paginator]

    def get(self, study_key: str, coding_id: str) -> Coding:
        """
        Get a specific coding by ID.

        Args:
            study_key: Study identifier
            coding_id: Coding identifier

        Returns:
            Coding object
        """
        path = self._build_path(study_key, "codings", coding_id)
        raw = self._client.get(path).json().get("data", [])
        if not raw:
            raise ValueError(f"Coding {coding_id} not found in study {study_key}")
        return Coding.from_json(raw[0])
