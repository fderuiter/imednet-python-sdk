"""Workflow utilities to build an enrollment dashboard."""

from typing import TYPE_CHECKING, Any, Dict, List

import pandas as pd

if TYPE_CHECKING:  # pragma: no cover - imported for type checking only
    from ..sdk import ImednetSDK


def build_dashboard(sdk: "ImednetSDK", study_key: str) -> pd.DataFrame:
    """Return a DataFrame summarizing enrollment by site.

    The dashboard includes each site's enrollment status, the number of
    subjects registered at the site, and the first/last enrollment dates.
    """

    # Retrieve all sites and subjects for the study
    sites = sdk.sites.list(study_key)
    subjects = sdk.subjects.list(study_key)

    site_lookup: Dict[int, Dict[str, Any]] = {}
    for site in sites:
        site_lookup[site.site_id] = {
            "site_name": site.site_name,
            "site_enrollment_status": site.site_enrollment_status,
            "subjects": [],
        }

    # Group subjects by site ID
    for subj in subjects:
        if subj.site_id not in site_lookup:
            continue
        site_lookup[subj.site_id]["subjects"].append(subj)

    rows: List[Dict[str, object]] = []
    for site_id, info in site_lookup.items():
        subj_list = info.pop("subjects")
        if subj_list:
            enroll_dates = [s.enrollment_start_date for s in subj_list]
            first = min(enroll_dates)
            last = max(enroll_dates)
        else:
            first = None
            last = None
        rows.append(
            {
                "site_id": site_id,
                "site_name": info["site_name"],
                "site_enrollment_status": info["site_enrollment_status"],
                "subject_count": len(subj_list),
                "first_enrollment": first,
                "last_enrollment": last,
            }
        )

    return pd.DataFrame(rows)
