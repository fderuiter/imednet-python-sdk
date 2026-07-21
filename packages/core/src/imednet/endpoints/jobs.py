"""Endpoint for checking job status in a study."""

from imednet.core.endpoint.dispatch import ExecuteOperation
from imednet.core.endpoint.edc_mixin import EdcAsyncListGetEndpoint, EdcSyncListGetEndpoint
from imednet.core.endpoint.operations.get import PathGetOperation
from imednet.core.paginator import AsyncJsonListPaginator, JsonListPaginator
from imednet.models.jobs import JobStatus
from imednet.utils.typing import ItemId


class JobsOperationDef:
    """Definition for Job operations."""

    PATH = "jobs"
    MODEL = JobStatus
    PAGINATOR_CLS = JsonListPaginator
    ASYNC_PAGINATOR_CLS = AsyncJsonListPaginator

    @ExecuteOperation  # type: ignore
    def get(self, study_key: str | None, item_id: ItemId) -> PathGetOperation[JobStatus]:
        """Get a single Job by ID."""
        self._require_item_id(item_id)  # type: ignore
        path = self._get_endpoint_path(study_key, item_id)  # type: ignore
        return PathGetOperation[JobStatus](
            path=path,
            parse_func=self._parse_item,  # type: ignore
            not_found_func=lambda: self._raise_not_found(study_key, item_id),  # type: ignore
        )


class JobsEndpoint(JobsOperationDef, EdcSyncListGetEndpoint[JobStatus]):  # type: ignore[misc]
    """Synchronous endpoint for managing Jobs."""


class AsyncJobsEndpoint(JobsOperationDef, EdcAsyncListGetEndpoint[JobStatus]):  # type: ignore[misc]
    """Asynchronous endpoint for managing Jobs."""
