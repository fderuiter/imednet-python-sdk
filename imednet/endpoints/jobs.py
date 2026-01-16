"""Endpoint for checking job status in a study."""

from typing import List

from imednet.core.paginator import AsyncListPaginator, ListPaginator
from imednet.endpoints._mixins import ListEndpointMixin
from imednet.endpoints.base import BaseEndpoint
from imednet.models.jobs import Job, JobStatus


class JobsEndpoint(ListEndpointMixin[Job], BaseEndpoint):
    """
    API endpoint for retrieving status and details of jobs in an iMedNet study.

    Provides a method to fetch a job by its batch ID.
    """

    PATH = "jobs"
    MODEL = Job
    paginator_cls = ListPaginator
    async_paginator_cls = AsyncListPaginator

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
        """
        endpoint = self._build_path(study_key, "jobs", batch_id)
        response = self._client.get(endpoint)
        data = response.json()
        if not data:
            raise ValueError(f"Job {batch_id} not found in study {study_key}")
        return JobStatus.from_json(data)

    async def async_get(self, study_key: str, batch_id: str) -> JobStatus:
        """Asynchronous version of :meth:`get`.

        Like the sync variant, it simply issues a request by ``batch_id``
        without any caching.
        """
        client = self._require_async_client()
        endpoint = self._build_path(study_key, "jobs", batch_id)
        response = await client.get(endpoint)
        data = response.json()
        if not data:
            raise ValueError(f"Job {batch_id} not found in study {study_key}")
        return JobStatus.from_json(data)

    def list(self, study_key: str) -> List[Job]:
        """
        List all jobs for a specific study.

        Args:
            study_key: Study identifier

        Returns:
            List of Job objects
        """
        return self._list_impl(
            self._client,
            self.paginator_cls,
            study_key=study_key,
        )

    async def async_list(self, study_key: str) -> List[Job]:
        """
        Asynchronously list all jobs for a specific study.

        Args:
            study_key: Study identifier

        Returns:
            List of Job objects
        """
        return await self._list_impl(
            self._require_async_client(),
            self.async_paginator_cls,
            study_key=study_key,
        )
