"""Endpoint for checking job status in a study."""

from typing import Optional

from imednet.core.endpoint.edc_mixin import EdcAsyncListGetEndpoint, EdcSyncListGetEndpoint
from imednet.core.endpoint.operations.get import PathGetOperation
from imednet.core.paginator import AsyncJsonListPaginator, JsonListPaginator
from imednet.models.jobs import JobStatus
from imednet.utils.typing import ItemId


class JobsEndpoint(EdcSyncListGetEndpoint[JobStatus]):
    """
    API endpoint for retrieving status and details of jobs in an iMedNet study.

    This endpoint provides methods to fetch individual job status by batch ID
    and list all jobs for a study.
    """

    PATH = "jobs"
    MODEL = JobStatus
    PAGINATOR_CLS = JsonListPaginator
    ASYNC_PAGINATOR_CLS = AsyncJsonListPaginator

    def _create_path_get_operation(
        self,
        study_key: Optional[str],
        item_id: ItemId,
    ) -> PathGetOperation[JobStatus]:
        path = self._get_endpoint_path(study_key, item_id)
        return PathGetOperation[JobStatus](
            path=path,
            parse_func=self._parse_item,
            not_found_func=lambda: self._raise_not_found(study_key, item_id),
        )

    def get(self, study_key: Optional[str], item_id: ItemId) -> JobStatus:
        self._require_item_id(item_id)
        return self._create_path_get_operation(study_key, item_id).execute_sync(
            self._require_sync_client()
        )


class AsyncJobsEndpoint(EdcAsyncListGetEndpoint[JobStatus]):
    PATH = "jobs"
    MODEL = JobStatus
    PAGINATOR_CLS = JsonListPaginator
    ASYNC_PAGINATOR_CLS = AsyncJsonListPaginator

    def _create_path_get_operation(
        self,
        study_key: Optional[str],
        item_id: ItemId,
    ) -> PathGetOperation[JobStatus]:
        path = self._get_endpoint_path(study_key, item_id)
        return PathGetOperation[JobStatus](
            path=path,
            parse_func=self._parse_item,
            not_found_func=lambda: self._raise_not_found(study_key, item_id),
        )

    async def async_get(self, study_key: Optional[str], item_id: ItemId) -> JobStatus:
        self._require_item_id(item_id)
        return await self._create_path_get_operation(study_key, item_id).execute_async(
            self._require_async_client()
        )
