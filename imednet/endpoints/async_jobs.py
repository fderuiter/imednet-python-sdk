"""Async endpoint for checking job status in a study."""

from imednet.core.async_client import AsyncClient
from imednet.endpoints.base import BaseEndpoint
from imednet.models.jobs import Job


class AsyncJobsEndpoint(BaseEndpoint[AsyncClient]):
    """Async API endpoint for retrieving job details."""

    path = "/api/v1/edc/studies"

    def __init__(self, client: AsyncClient, ctx) -> None:
        super().__init__(client, ctx)

    async def get(self, study_key: str, batch_id: str) -> Job:
        endpoint = self._build_path(study_key, "jobs", batch_id)
        response = await self._client.get(endpoint)
        data = response.json()
        if not data:
            raise ValueError(f"Job {batch_id} not found in study {study_key}")
        return Job.from_json(data)
