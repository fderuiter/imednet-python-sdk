"""Endpoint for managing subjects in a study."""

from typing import List

from imednet.core.endpoint.edc_mixin import EdcAsyncListGetEndpoint, EdcSyncListGetEndpoint
from imednet.models.subjects import Subject


class SubjectsOperationDef:
    """Definition for Subject operations."""

    PATH = "subjects"
    MODEL = Subject
    _id_param = "subjectKey"


class SubjectsEndpoint(SubjectsOperationDef, EdcSyncListGetEndpoint[Subject]):  # type: ignore[misc]
    """Synchronous endpoint for managing Subjects."""

    def list_by_site(self, study_key: str, site_id: str | int) -> List[Subject]:
        """List subjects by site ID.

        Args:
            study_key: The study key.
            site_id: The site ID or site key.

        Returns:
            A list of subjects for the specified site.
        """
        return list(self.list(study_key=study_key, site_id=site_id))


class AsyncSubjectsEndpoint(SubjectsOperationDef, EdcAsyncListGetEndpoint[Subject]):  # type: ignore[misc]
    """Asynchronous endpoint for managing Subjects."""

    async def async_list_by_site(
        self, study_key: str, site_id: str | int
    ) -> List[Subject]:
        """List subjects by site ID asynchronously.

        Args:
            study_key: The study key.
            site_id: The site ID or site key.

        Returns:
            A list of subjects for the specified site.
        """
        return [
            item async for item in self.async_list(study_key=study_key, site_id=site_id)
        ]
