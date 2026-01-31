"""Endpoint for managing subjects in a study."""

from typing import List

from imednet.endpoints._mixins import ListGetEndpoint
from imednet.models.subjects import Subject


class SubjectsEndpoint(ListGetEndpoint[Subject]):
    """
    API endpoint for interacting with subjects in an iMedNet study.

    Provides methods to list and retrieve individual subjects.
    """

    PATH = "subjects"
    MODEL = Subject
    _id_param = "subjectKey"

    def _filter_by_site(
        self, subjects: List[Subject], site_id: str | int
    ) -> List[Subject]:
        """Filter subjects by site ID using strict string comparison."""
        target_site = str(site_id)
        return [s for s in subjects if str(s.site_id) == target_site]

    def list_by_site(self, study_key: str, site_id: str | int) -> List[Subject]:
        """
        List subjects filtered by a specific site ID.

        Migrated from TUI logic to core SDK to support filtering.
        """
        all_subjects = self.list(study_key)
        return self._filter_by_site(all_subjects, site_id)

    async def async_list_by_site(self, study_key: str, site_id: str | int) -> List[Subject]:
        """Asynchronously list subjects filtered by a specific site ID."""
        all_subjects = await self.async_list(study_key)
        return self._filter_by_site(all_subjects, site_id)
