"""Endpoint for managing intervals (visit definitions) in a study."""

from typing import Any, List, Optional, cast

from imednet.core.paginator import Paginator
from imednet.endpoints.base import BaseEndpoint
from imednet.endpoints.helpers import build_paginator
from imednet.models.intervals import Interval


class IntervalsEndpoint(BaseEndpoint):
    """
    API endpoint for interacting with intervals (visit definitions) in an iMedNet study.

    Provides methods to list and retrieve individual intervals.
    """

    path = "/api/v1/edc/studies"

    def list(
        self,
        study_key: Optional[str] = None,
        page_size: Optional[int] = None,
        **filters: Any,
    ) -> List[Interval]:
        """
        List intervals in a study with optional filtering.

        Args:
            study_key: Study identifier (uses default from context if not specified)
            ``**filters``: Additional filter parameters

        Returns:
            List of Interval objects
        """
        paginator = cast(
            Paginator,
            build_paginator(
                self,
                Paginator,
                "intervals",
                study_key,
                page_size,
                filters,
            ),
        )
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
