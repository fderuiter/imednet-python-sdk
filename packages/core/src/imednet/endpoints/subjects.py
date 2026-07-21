"""Endpoint for managing subjects in a study."""

from typing import Any

from imednet.core.endpoint.dispatch import ExecuteOperation
from imednet.core.endpoint.edc_mixin import EdcAsyncListGetEndpoint, EdcSyncListGetEndpoint
from imednet.models.subjects import Subject


class ListBySiteOperation:
    """List subjects by site ID operation."""

    def __init__(self, endpoint: Any, study_key: str, site_id: str | int):
        """Initialize."""
        self.endpoint = endpoint
        self.study_key = study_key
        self.site_id = site_id

    def execute_sync(self, client: Any, parse_func: Any = None) -> list[Subject]:
        """Execute synchronously."""
        return list(
            self.endpoint._list_sync(
                client, self.endpoint.PAGINATOR_CLS, study_key=self.study_key, site_id=self.site_id
            )
        )

    async def execute_async(self, client: Any, parse_func: Any = None) -> list[Subject]:
        """Execute asynchronously."""
        res = []
        async for item in self.endpoint._list_async(
            client,
            self.endpoint.ASYNC_PAGINATOR_CLS,
            study_key=self.study_key,
            site_id=self.site_id,
        ):
            res.append(item)
        return res


class SubjectsOperationDef:
    """Definition for Subject operations."""

    PATH = "subjects"
    MODEL = Subject
    _id_param = "subjectKey"

    @ExecuteOperation  # type: ignore
    def list_by_site(self, study_key: str, site_id: str | int) -> ListBySiteOperation:
        """List subjects by site ID."""
        return ListBySiteOperation(self, study_key, site_id)


class SubjectsEndpoint(SubjectsOperationDef, EdcSyncListGetEndpoint[Subject]):  # type: ignore[misc]
    """Synchronous endpoint for managing Subjects."""


class AsyncSubjectsEndpoint(SubjectsOperationDef, EdcAsyncListGetEndpoint[Subject]):  # type: ignore[misc]
    """Asynchronous endpoint for managing Subjects."""
