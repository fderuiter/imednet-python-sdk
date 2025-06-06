"""Workflow to summarize subject enrollment and dropout rates by site."""

from typing import TYPE_CHECKING, Any, Dict, List

import pandas as pd

if TYPE_CHECKING:  # pragma: no cover - import for type checking only
    from ..sdk import ImednetSDK


DROPOUT_STATUSES = {"WITHDRAWN", "DROPPED", "SCREENFAIL"}


class SubjectEnrollmentDashboard:
    """Build a dashboard combining site and subject enrollment information."""

    def __init__(self, sdk: "ImednetSDK") -> None:
        self._sdk = sdk

    def build(self, study_key: str) -> pd.DataFrame:
        """Return a DataFrame summarizing enrollment and dropout metrics."""
        sites = self._sdk.sites.list(study_key)
        subjects = self._sdk.subjects.list(study_key)

        site_lookup: Dict[int, Dict[str, Any]] = {}
        for site in sites:
            site_lookup[site.site_id] = {
                "site_name": site.site_name,
                "site_enrollment_status": site.site_enrollment_status,
                "subjects": [],
            }

        for subj in subjects:
            if subj.site_id in site_lookup:
                site_lookup[subj.site_id]["subjects"].append(subj)

        rows: List[Dict[str, object]] = []
        for site_id, info in site_lookup.items():
            subj_list = info.pop("subjects")
            first = min((s.enrollment_start_date for s in subj_list), default=None)
            last = max((s.enrollment_start_date for s in subj_list), default=None)
            dropout_count = sum(
                1 for s in subj_list if s.subject_status.upper() in DROPOUT_STATUSES
            )
            total = len(subj_list)
            rows.append(
                {
                    "site_id": site_id,
                    "site_name": info["site_name"],
                    "site_enrollment_status": info["site_enrollment_status"],
                    "subject_count": total,
                    "dropout_count": dropout_count,
                    "dropout_rate": dropout_count / total if total else 0.0,
                    "first_enrollment": first,
                    "last_enrollment": last,
                }
            )

        return pd.DataFrame(rows)
