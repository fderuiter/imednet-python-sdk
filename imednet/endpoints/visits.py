"""Endpoint for managing visits (interval instances) in a study."""

from typing import Any, Dict, List, Optional

from imednet.core.paginator import Paginator
from imednet.endpoints.base import BaseEndpoint
from imednet.models.visits import Visit
from imednet.utils.filters import build_filter_string


class VisitsEndpoint(BaseEndpoint):
    """
    API endpoint for interacting with visits (interval instances) in an iMedNet study.

    Provides methods to list and retrieve individual visits.
    """

    path = "/api/v1/edc/studies"

    def list(self, study_key: Optional[str] = None, **filters) -> List[Visit]:
        """
        List visits in a study with optional filtering.

        Args:
            study_key: Study identifier (uses default from context if not specified)
            **filters: Additional filter parameters

        Returns:
            List of Visit objects
        """
        filters = self._auto_filter(filters)
        if study_key:
            filters["studyKey"] = study_key

        params: Dict[str, Any] = {}
        if filters:
            params["filter"] = build_filter_string(filters)

        path = self._build_path(filters.get("studyKey", ""), "visits")
        paginator = Paginator(self._client, path, params=params)
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


__all__ = ["VisitsEndpoint"]
