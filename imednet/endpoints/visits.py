"""Endpoint for managing visits (interval instances) in a study."""

from typing import Any, List, Optional, cast

from imednet.core.paginator import Paginator
from imednet.endpoints.base import BaseEndpoint
from imednet.endpoints.helpers import build_paginator
from imednet.models.visits import Visit


class VisitsEndpoint(BaseEndpoint):
    """
    API endpoint for interacting with visits (interval instances) in an iMedNet study.

    Provides methods to list and retrieve individual visits.
    """

    path = "/api/v1/edc/studies"

    def list(
        self,
        study_key: Optional[str] = None,
        page_size: Optional[int] = None,
        **filters: Any,
    ) -> List[Visit]:
        """
        List visits in a study with optional filtering.

        Args:
            study_key: Study identifier (uses default from context if not specified)
            ``**filters``: Additional filter parameters

        Returns:
            List of Visit objects
        """
        paginator = cast(
            Paginator,
            build_paginator(
                self,
                Paginator,
                "visits",
                study_key,
                page_size,
                filters,
            ),
        )
        return [Visit.from_json(item) for item in paginator]

    def get(self, study_key: str, visit_id: int) -> Visit:
        """
        Get a specific visit by ID.

        Args:
            study_key: Study identifier
            visit_id: Visit identifier

        Returns:
            Visit object
        """
        path = self._build_path(study_key, "visits", visit_id)
        raw = self._client.get(path).json().get("data", [])
        if not raw:
            raise ValueError(f"Visit {visit_id} not found in study {study_key}")
        return Visit.from_json(raw[0])
