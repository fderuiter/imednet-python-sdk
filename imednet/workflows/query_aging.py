"""Provides utilities for analyzing the age of open queries."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any, Dict, List, Optional

from .query_management import QueryManagementWorkflow

if TYPE_CHECKING:  # pragma: no cover - type checking only
    from ..sdk import ImednetSDK


class QueryAgingWorkflow:
    """Workflow for summarizing open query aging information."""

    def __init__(self, sdk: "ImednetSDK") -> None:
        self._sdk = sdk
        self._qm = QueryManagementWorkflow(sdk)

    def aging_summary(
        self,
        study_key: str,
        buckets: Optional[List[int]] = None,
        **kwargs: Any,
    ) -> Dict[str, int]:
        """Return counts of open queries grouped by age buckets.

        Args:
            study_key: Identifier of the study.
            buckets: Sorted list of day thresholds. Defaults to ``[7, 14, 30]``.
            **kwargs: Additional keyword arguments passed to
                :meth:`QueryManagementWorkflow.get_open_queries`.

        Returns:
            Mapping of bucket labels to counts, e.g. ``{"0-7": 5, ">30": 2}``.
        """
        if buckets is None:
            buckets = [7, 14, 30]
        buckets = sorted(buckets)

        open_queries = self._qm.get_open_queries(study_key, **kwargs)
        now = datetime.now(timezone.utc)

        summary: Dict[str, int] = {}
        start = 0
        for end in buckets:
            summary[f"{start}-{end}"] = 0
            start = end + 1
        summary[f">{buckets[-1]}"] = 0

        for query in open_queries:
            age = (now - query.date_created).days
            start = 0
            placed = False
            for end in buckets:
                if age <= end:
                    summary[f"{start}-{end}"] += 1
                    placed = True
                    break
                start = end + 1
            if not placed:
                summary[f">{buckets[-1]}"] += 1

        return summary
