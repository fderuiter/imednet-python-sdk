"""Custom logic mixins for Subjects endpoint."""

from typing import List
from imednet.models.subjects import Subject

class SubjectsMixin:
    def list_by_site(self, study_key: str, site_id: str | int) -> List[Subject]:
        return list(self.list(study_key=study_key, site_id=site_id))

class AsyncSubjectsMixin:
    async def async_list_by_site(self, study_key: str, site_id: str | int) -> List[Subject]:
        return [item async for item in self.async_list(study_key=study_key, site_id=site_id)]
