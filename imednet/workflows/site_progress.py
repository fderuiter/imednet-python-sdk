"""Workflows for assessing enrollment and query progress at the site level."""

from __future__ import annotations

from typing import TYPE_CHECKING, List

from pydantic import BaseModel, ConfigDict, Field

if TYPE_CHECKING:
    from ..sdk import ImednetSDK


class SiteProgress(BaseModel):
    """Aggregated progress metrics for a single site."""

    site_id: int = Field(..., alias="siteId")
    site_name: str = Field(..., alias="siteName")
    subjects_enrolled: int
    visits_completed: int
    open_queries: int

    model_config = ConfigDict(populate_by_name=True)


class SiteProgressWorkflow:
    """Workflow for computing site level progress statistics."""

    def __init__(self, sdk: "ImednetSDK"):
        self._sdk = sdk

    def get_site_progress(self, study_key: str) -> List[SiteProgress]:
        """Return enrollment, visit and query counts for all sites in a study."""
        sites = self._sdk.sites.list(study_key)
        results: List[SiteProgress] = []
        for site in sites:
            subjects = self._sdk.subjects.list(study_key, site_id=site.site_id)
            subject_keys = [s.subject_key for s in subjects]

            visits_completed = 0
            for subj_key in subject_keys:
                visits = self._sdk.visits.list(study_key, subject_key=subj_key)
                visits_completed += sum(1 for v in visits if v.visit_date is not None)

            open_queries = 0
            for subj_key in subject_keys:
                queries = self._sdk.queries.list(study_key, subject_key=subj_key)
                for q in queries:
                    if not q.query_comments:
                        continue
                    latest = max(q.query_comments, key=lambda c: c.sequence)
                    if not latest.closed:
                        open_queries += 1

            results.append(
                SiteProgress(
                    site_id=site.site_id,
                    site_name=site.site_name,
                    subjects_enrolled=len(subjects),
                    visits_completed=visits_completed,
                    open_queries=open_queries,
                )
            )
        return results
