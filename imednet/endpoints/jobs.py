"""Endpoint for checking job status in a study."""

from typing import Optional

from imednet.endpoints.base import BaseEndpoint
from imednet.models.jobs import Job


class JobsEndpoint(BaseEndpoint):
    """
    API endpoint for checking the status of background jobs in an iMedNet study.

    Jobs are created by operations such as POST requests to the Records endpoint.
    """

    path = "/api/v1/edc/studies"

    def get_status(self, study_key: Optional[str], batch_id: str) -> Job:
        """
        Get the status of a specific job by its batch ID.

        Args:
            study_key: Study identifier (uses default from context if not specified)
            batch_id: Batch identifier returned from a POST request

        Returns:
            Job object with current state of the job
        """
        study_key = study_key or self._ctx.default_study_key
        if not study_key:
            raise ValueError("Study key must be provided or set in the context")

        path = self._build_path(study_key, "jobs", batch_id)
        response = self._client.get(path)

        # Convert the JSON response to a Job object
        data = response.json()
        from datetime import datetime

        return Job(
            job_id=data.get("jobId", ""),
            batch_id=data.get("batchId", ""),
            state=data.get("state", ""),
            date_created=datetime.fromisoformat(data.get("dateCreated", "").replace(" ", "T")),
            date_started=datetime.fromisoformat(data.get("dateStarted", "").replace(" ", "T")),
            date_finished=datetime.fromisoformat(data.get("dateFinished", "").replace(" ", "T")),
        )
