"""Endpoint for checking job status in a study."""

from typing import Any, Optional

from imednet.core.endpoint.mixins import EdcListPathGetEndpoint
from imednet.core.paginator import AsyncJsonListPaginator, JsonListPaginator
from imednet.models.jobs import JobStatus


class JobsEndpoint(EdcListPathGetEndpoint[JobStatus]):
    """
    API endpoint for retrieving status and details of jobs in an iMedNet study.

    This endpoint provides methods to fetch individual job status by batch ID
    and list all jobs for a study.
    """

    PATH = "jobs"
    MODEL = JobStatus
    PAGINATOR_CLS = JsonListPaginator
    ASYNC_PAGINATOR_CLS = AsyncJsonListPaginator

    def _raise_not_found(self, study_key: Optional[str], item_id: Any) -> None:
        raise ValueError(f"Job {item_id} not found in study {study_key}")
