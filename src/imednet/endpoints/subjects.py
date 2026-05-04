"""Endpoint for managing subjects in a study."""

from typing import List

from imednet.core.endpoint.base import GenericListGetEndpoint
from imednet.core.endpoint.edc_mixin import EdcEndpointMixin
from imednet.models.subjects import Subject


class SubjectsEndpoint(
    EdcEndpointMixin,
    GenericListGetEndpoint[Subject],
):
    """
    API endpoint for interacting with subjects in an iMedNet study.

    Provides methods to list and retrieve individual subjects.
    """

    PATH = "subjects"
    MODEL = Subject
    _id_param = "subjectKey"

    def list_by_site(self, study_key: str, site_id: str | int) -> List[Subject]:
        """
        List subjects filtered by a specific site ID.

        Migrated from TUI logic to core SDK to support filtering.
        """
        return self.list(study_key=study_key, site_id=site_id)

    async def async_list_by_site(self, study_key: str, site_id: str | int) -> List[Subject]:
        """Asynchronously list subjects filtered by a specific site ID."""
        return await self.async_list(study_key=study_key, site_id=site_id)
