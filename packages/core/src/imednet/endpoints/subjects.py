"""Endpoint for managing subjects in a study."""

from typing import List

from imednet.core.endpoint.edc_mixin import EdcAsyncListGetEndpoint, EdcSyncListGetEndpoint
from imednet.models.subjects import Subject


class SubjectsOperationDef:
    PATH = "subjects"
    MODEL = Subject
    _id_param = "subjectKey"

class SubjectsEndpoint(SubjectsOperationDef, EdcSyncListGetEndpoint[Subject]): # type: ignore[misc]
    def list_by_site(self, study_key: str, site_id: str | int) -> List[Subject]:
        return list(self.list(study_key=study_key, site_id=site_id))

class AsyncSubjectsEndpoint(SubjectsOperationDef, EdcAsyncListGetEndpoint[Subject]): # type: ignore[misc]
    async def async_list_by_site(self, study_key: str, site_id: str | int) -> List[Subject]:
        return [item async for item in self.async_list(study_key=study_key, site_id=site_id)]
