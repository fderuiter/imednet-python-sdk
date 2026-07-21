"""Endpoint for managing subjects in a study."""

from imednet.core.endpoint.dispatch import execute_operation
from imednet.core.endpoint.edc_mixin import EdcAsyncListGetEndpoint, EdcSyncListGetEndpoint
from imednet.models.subjects import Subject
from typing import Any

class ListBySiteOperation:
    def __init__(self, endpoint: Any, study_key: str, site_id: str | int):
        self.endpoint = endpoint
        self.study_key = study_key
        self.site_id = site_id

    def execute_sync(self, client: Any, parse_func: Any = None) -> list[Subject]:
        return list(self.endpoint._list_sync(client, self.endpoint.PAGINATOR_CLS, study_key=self.study_key, site_id=self.site_id))

    async def execute_async(self, client: Any, parse_func: Any = None) -> list[Subject]:
        res = []
        async for item in self.endpoint._list_async(client, self.endpoint.ASYNC_PAGINATOR_CLS, study_key=self.study_key, site_id=self.site_id):
            res.append(item)
        return res

class SubjectsOperationDef:
    """Definition for Subject operations."""

    PATH = "subjects"
    MODEL = Subject
    _id_param = "subjectKey"

    @execute_operation  # type: ignore
    def list_by_site(self, study_key: str, site_id: str | int) -> ListBySiteOperation:
        """List subjects by site ID."""
        return ListBySiteOperation(self, study_key, site_id)

class SubjectsEndpoint(SubjectsOperationDef, EdcSyncListGetEndpoint[Subject]):  # type: ignore[misc]
    """Synchronous endpoint for managing Subjects."""

class AsyncSubjectsEndpoint(SubjectsOperationDef, EdcAsyncListGetEndpoint[Subject]):  # type: ignore[misc]
    """Asynchronous endpoint for managing Subjects."""
