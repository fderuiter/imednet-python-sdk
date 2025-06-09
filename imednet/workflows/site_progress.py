"""Workflow for summarizing progress metrics per site."""

from __future__ import annotations

from typing import TYPE_CHECKING, List

from pydantic import BaseModel, ConfigDict, Field

if TYPE_CHECKING:
    from ..sdk import ImednetSDK


class SiteProgress(BaseModel):
    """Aggregated progress metrics for a site."""

    site_id: int = Field(0, alias="siteId")
    site_name: str = Field("", alias="siteName")
    subjects_enrolled: int = 0
    visits_completed: int = 0
    open_queries: int = 0

    model_config = ConfigDict(populate_by_name=True)


class SiteProgressWorkflow:
    """Workflow providing progress statistics for each site in a study."""

    def __init__(self, sdk: "ImednetSDK") -> None:
        self._sdk = sdk

    def get_site_progress(self, study_key: str) -> List[SiteProgress]:
        """Return progress metrics for all sites in the study."""
        sites = self._sdk.sites.list(study_key)
        results: List[SiteProgress] = []

        for site in sites:
            subjects = self._sdk.subjects.list(study_key, site_id=site.site_id)
            subject_keys = [s.subject_key for s in subjects]

            visits_completed = 0
            open_queries = 0

            if subject_keys:
                visits = self._sdk.visits.list(study_key, subject_key=subject_keys)
                visits_completed = len([v for v in visits if v.visit_date is not None])

                queries = self._sdk.queries.list(study_key, subject_key=subject_keys)
                for q in queries:
                    if not q.query_comments:
                        continue
                    latest_comment = max(q.query_comments, key=lambda c: c.sequence)
                    if not latest_comment.closed:
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
