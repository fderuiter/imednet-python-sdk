"""Endpoint for checking job status in a study."""

from typing import Awaitable, Optional, Union, overload

from imednet.core.endpoint.edc_mixin import ClientT, EdcListGetEndpoint
from imednet.core.endpoint.operations.get import PathGetOperation
from imednet.core.paginator import AsyncJsonListPaginator, JsonListPaginator
from imednet.core.protocols import AsyncRequestorProtocol, RequestorProtocol
from imednet.models.jobs import JobStatus
from imednet.utils.typing import ItemId


class JobsOperationDef:
    """TODO: Add docstring."""

    PATH = "jobs"
    MODEL = JobStatus
    PAGINATOR_CLS = JsonListPaginator
    ASYNC_PAGINATOR_CLS = AsyncJsonListPaginator

    def _create_path_get_operation(
        self,
        study_key: Optional[str],
        item_id: ItemId,
    ) -> PathGetOperation[JobStatus]:
        """TODO: Add docstring."""
        path = self._get_endpoint_path(study_key, item_id)  # type: ignore
        return PathGetOperation[JobStatus](
            path=path,
            parse_func=self._parse_item,  # type: ignore
            not_found_func=lambda: self._raise_not_found(study_key, item_id),  # type: ignore
        )


class JobsEndpoint(JobsOperationDef, EdcListGetEndpoint[JobStatus, ClientT]):  # type: ignore[misc]
    """TODO: Add docstring."""

    @overload
    def get(self: "JobsEndpoint[RequestorProtocol]", study_key: Optional[str], item_id: ItemId) -> JobStatus: ...

    @overload
    def get(self: "JobsEndpoint[AsyncRequestorProtocol]", study_key: Optional[str], item_id: ItemId) -> Awaitable[JobStatus]: ...

    def get(self, study_key: Optional[str], item_id: ItemId) -> Union[JobStatus, Awaitable[JobStatus]]:
        """TODO: Add docstring."""
        self._require_item_id(item_id)
        operation = self._create_path_get_operation(study_key, item_id)
        if self._async_client:
            return operation.execute_async(self._require_async_client())
        else:
            return operation.execute_sync(self._require_sync_client())

class AsyncJobsEndpoint(JobsEndpoint):  # type: ignore[misc]
    """Legacy backwards-compatible async endpoint."""
    def __init__(self, client, ctx=None):
        """TODO: Add docstring."""
        super().__init__(client, ctx=ctx)
        self._async_client = client
