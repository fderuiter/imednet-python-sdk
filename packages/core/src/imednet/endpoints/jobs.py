"""Endpoint for checking job status in a study."""

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

    def _create_path_get_operation(
        self,
        study_key: str | None,
        item_id: ItemId,
    ) -> PathGetOperation[JobStatus]:
        """Create a PathGetOperation for a Job.

        Args:
            study_key: The study key.
            item_id: The job ID (batch ID).

        Returns:
            The get operation.
        """
        path = self._get_endpoint_path(study_key, item_id)  # type: ignore
        return PathGetOperation[JobStatus](
            path=path,
            parse_func=self._parse_item,  # type: ignore
            not_found_func=lambda: self._raise_not_found(study_key, item_id),  # type: ignore
        )


class JobsEndpoint(JobsOperationDef, EdcSyncListGetEndpoint[JobStatus]):  # type: ignore[misc]
    """Synchronous endpoint for managing Jobs."""

    def get(self, study_key: str | None, item_id: ItemId) -> JobStatus:
        """Get a single Job by ID.

        Args:
            study_key: The study key.
            item_id: The job ID (batch ID).

        Returns:
            The job status.
        """
        self._require_item_id(item_id)
        return self._create_path_get_operation(study_key, item_id).execute_sync(
            self._require_sync_client()
        )


class AsyncJobsEndpoint(JobsOperationDef, EdcAsyncListGetEndpoint[JobStatus]):  # type: ignore[misc]
    """Asynchronous endpoint for managing Jobs."""

    async def async_get(self, study_key: str | None, item_id: ItemId) -> JobStatus:
        """Get a single Job by ID asynchronously.

        Args:
            study_key: The study key.
            item_id: The job ID (batch ID).

        Returns:
            The job status.
        """
        self._require_item_id(item_id)
        return await self._create_path_get_operation(study_key, item_id).execute_async(
            self._require_async_client()
        )
