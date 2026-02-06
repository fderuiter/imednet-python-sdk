"""Endpoint for checking job status in a study."""

import inspect
from typing import Any, Awaitable, List, Optional, cast

from imednet.core.endpoint.base import BaseEndpoint
from imednet.core.endpoint.mixins import PathGetEndpointMixin
from imednet.core.parsing import get_model_parser
from imednet.core.protocols import AsyncRequestorProtocol, RequestorProtocol
from imednet.models.jobs import Job, JobStatus


class JobsEndpoint(BaseEndpoint, PathGetEndpointMixin[JobStatus]):
    """
    API endpoint for retrieving status and details of jobs in an iMedNet study.

    This endpoint provides methods to fetch individual job status by batch ID
    and list all jobs for a study.
    """

    PATH = "jobs"
    MODEL = JobStatus

    def _raise_not_found(self, study_key: Optional[str], item_id: Any) -> None:
        raise ValueError(f"Job {item_id} not found in study {study_key}")

    def get(self, study_key: str, batch_id: str) -> JobStatus:
        """
        Get a specific job by batch ID.

        This method performs a direct API request using the provided
        ``batch_id``; it does not use caching or the ``refresh`` flag.

        Args:
            study_key: Study identifier
            batch_id: Batch ID of the job

        Returns:
            JobStatus object with current state and timestamps

        Raises:
            ValueError: If the job is not found
        """
        return cast(
            JobStatus,
            self._get_impl_path(self._client, study_key=study_key, item_id=batch_id),
        )

    async def async_get(self, study_key: str, batch_id: str) -> JobStatus:
        """
        Asynchronously get a specific job by batch ID.

        This is the async variant of :meth:`get`. Like the sync version,
        it issues a direct request by ``batch_id`` without any caching.

        Args:
            study_key: Study identifier
            batch_id: Batch ID of the job

        Returns:
            JobStatus object with current state and timestamps

        Raises:
            ValueError: If the job is not found
        """
        client = self._require_async_client()
        return await cast(
            Awaitable[JobStatus],
            self._get_impl_path(client, study_key=study_key, item_id=batch_id),
        )

    def _execute_list_request(
        self,
        client: RequestorProtocol | AsyncRequestorProtocol,
        study_key: str,
    ) -> List[Job] | Awaitable[List[Job]]:
        endpoint = self._build_path(study_key, self.PATH)
        parser = get_model_parser(Job)

        if inspect.iscoroutinefunction(client.get):

            async def _await() -> List[Job]:
                c = cast(AsyncRequestorProtocol, client)
                response = await c.get(endpoint)
                return [parser(item) for item in response.json()]

            return _await()

        c = cast(RequestorProtocol, client)
        response = c.get(endpoint)
        return [parser(item) for item in response.json()]

    def list(self, study_key: str) -> List[Job]:
        """
        List all jobs for a specific study.

        Args:
            study_key: Study identifier

        Returns:
            List of Job objects
        """
        return cast(List[Job], self._execute_list_request(self._client, study_key))

    async def async_list(self, study_key: str) -> List[Job]:
        """
        Asynchronously list all jobs for a specific study.

        Args:
            study_key: Study identifier

        Returns:
            List of Job objects
        """
        client = self._require_async_client()
        return await cast(Awaitable[List[Job]], self._execute_list_request(client, study_key))
