"""Workflow for summarizing site-level performance metrics."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, List

import pandas as pd

from .query_management import QueryManagementWorkflow

if TYPE_CHECKING:  # pragma: no cover - imported for type checking only
    from ..sdk import ImednetSDK


class SitePerformanceWorkflow:
    """Provide methods for aggregating site-level metrics."""

    def __init__(self, sdk: "ImednetSDK") -> None:
        self._sdk = sdk
        self._queries = QueryManagementWorkflow(sdk)

    def get_site_metrics(self, study_key: str) -> pd.DataFrame:
        """Return enrollment and query counts grouped by site."""
        sites = self._sdk.sites.list(study_key)
        subjects = self._sdk.subjects.list(study_key)
        subject_lookup: Dict[int, Any] = {s.subject_id: s for s in subjects}
        open_queries = self._queries.get_open_queries(study_key)

        rows: List[Dict[str, Any]] = []
        for site in sites:
            subj_count = sum(1 for s in subjects if s.site_id == site.site_id)
            open_count = sum(
                1
                for q in open_queries
                if subject_lookup.get(q.subject_id)
                and subject_lookup[q.subject_id].site_id == site.site_id
            )
            rows.append(
                {
                    "site_id": site.site_id,
                    "site_name": site.site_name,
                    "site_enrollment_status": site.site_enrollment_status,
                    "subject_count": subj_count,
                    "open_query_count": open_count,
                }
            )

        return pd.DataFrame(rows)
