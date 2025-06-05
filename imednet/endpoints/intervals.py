"""Endpoint for managing intervals (visit definitions) in a study."""

from typing import Any, Dict, List, Optional

from imednet.core.paginator import Paginator
from imednet.endpoints.base import BaseEndpoint
from imednet.models.intervals import Interval
from imednet.utils.filters import build_filter_string


class IntervalsEndpoint(BaseEndpoint):
    """
    API endpoint for interacting with intervals (visit definitions) in an iMedNet study.

    Provides methods to list and retrieve individual intervals.
    """

    path = "/api/v1/edc/studies"

    def list(self, study_key: Optional[str] = None, **filters: Any) -> List[Interval]:
        """
        List intervals in a study with optional filtering.

        Args:
            study_key: Study identifier (uses default from context if not specified)
            ``**filters``: Additional filter parameters

        Returns:
            List of Interval objects
        """
        filters = self._auto_filter(filters)
        if study_key:
            filters["studyKey"] = study_key

        params: Dict[str, Any] = {}
        if filters:
            params["filter"] = build_filter_string(filters)

        path = self._build_path(filters.get("studyKey", ""), "intervals")
        paginator = Paginator(self._client, path, params=params, page_size=500)
        return [Interval.from_json(item) for item in paginator]

    def get(self, study_key: str, interval_id: int) -> Interval:
        """
        Get a specific interval by ID.

        Args:
            study_key: Study identifier
            interval_id: Interval identifier

        Returns:
            Interval object
        """
        path = self._build_path(study_key, "intervals", interval_id)
        raw = self._client.get(path).json().get("data", [])
        if not raw:
            raise ValueError(f"Interval {interval_id} not found in study {study_key}")
        return Interval.from_json(raw[0])
