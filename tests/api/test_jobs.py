# Tests for the Jobs API client.

from datetime import datetime  # Import datetime

import pytest
import respx
from httpx import Response

from imednet_sdk.client import ImednetClient
# The client method should return JobStatusModel directly based on docs
from imednet_sdk.models.job import JobStatusModel

# ApiResponse might not be needed if the client returns the model directly
# from imednet_sdk.models._common import ApiResponse


@pytest.fixture
def client():
    """Fixture for ImednetClient."""

    return ImednetClient(api_key="test_key", security_key="test_sec_key")


@pytest.fixture
def jobs_client(client):
    """Fixture for JobsClient."""

    return client.jobs  # Assuming integration in main client later


@respx.mock
def test_get_job_status_success(jobs_client, client):
    """Test successful retrieval of job status."""
    study_key = "MOCK-STUDY"  # Use example from docs
    batch_id = "75e63db6-fa41-40bc-b939-cf3bdb246ae8"  # Use example from docs
    mock_url = f"{client.base_url}/api/v1/edc/studies/{study_key}/jobs/{batch_id}"
    # Corrected mock response based on docs/reference/jobs.md
    mock_response_data = {
        "jobId": "afa2d61e-07ed-4efe-99c5-6f358f5e7d38",  # Use example from docs
        "batchId": batch_id,
        "state": "completed",  # Lowercase as per docs
        "dateCreated": "2020-12-01 21:47:36",  # Use example format
        "dateStarted": "2020-12-01 21:47:42",
        "dateFinished": "2020-12-01 21:47:45",
    }
    # The endpoint returns the job status object directly
    respx.get(mock_url).mock(return_value=Response(200, json=mock_response_data))

    # Assuming jobs_client.get_job_status is updated to return JobStatusModel directly
    response = jobs_client.get_job_status(study_key=study_key, batch_id=batch_id)

    # Assert the response is the JobStatusModel directly
    assert isinstance(response, JobStatusModel)
    # Assertions based on corrected mock data and documented fields
    assert response.jobId == "afa2d61e-07ed-4efe-99c5-6f358f5e7d38"
    assert response.batchId == batch_id
    assert response.state == "completed"
    # Compare datetime objects after parsing
    datetime_format = "%Y-%m-%d %H:%M:%S"
    assert response.dateCreated == datetime.strptime("2020-12-01 21:47:36", datetime_format)
    assert response.dateStarted == datetime.strptime("2020-12-01 21:47:42", datetime_format)
    assert response.dateFinished == datetime.strptime("2020-12-01 21:47:45", datetime_format)


@respx.mock
def test_get_job_status_running(jobs_client, client):  # Renamed for clarity
    """Test retrieval of job status when running."""
    study_key = "STUDYBATCH"
    batch_id = "BATCHRUNNING"
    mock_url = f"{client.base_url}/api/v1/edc/studies/{study_key}/jobs/{batch_id}"
    # Mock response for a 'running' state based on docs structure
    mock_response_data = {
        "jobId": "JOBRUN1",
        "batchId": batch_id,
        "state": "running",  # Lowercase as per docs
        "dateCreated": "2023-11-01 11:00:00",
        "dateStarted": "2023-11-01 11:00:05",
        "dateFinished": None,  # Should be None if running
    }
    respx.get(mock_url).mock(return_value=Response(200, json=mock_response_data))

    response = jobs_client.get_job_status(study_key=study_key, batch_id=batch_id)

    assert isinstance(response, JobStatusModel)
    assert response.batchId == batch_id
    assert response.state == "running"
    assert response.dateStarted is not None
    assert response.dateFinished is None  # Check that finished date is None


def test_get_job_status_missing_study_key(jobs_client):
    """Test get_job_status with missing study_key raises ValueError."""

    with pytest.raises(ValueError, match="study_key is required."):

        jobs_client.get_job_status(study_key="", batch_id="BATCH123")

    with pytest.raises(ValueError, match="study_key is required."):

        jobs_client.get_job_status(study_key=None, batch_id="BATCH123")  # type: ignore


def test_get_job_status_missing_batch_id(jobs_client):
    """Test get_job_status with missing batch_id raises ValueError."""

    with pytest.raises(ValueError, match="batch_id is required."):

        jobs_client.get_job_status(study_key="STUDY123", batch_id="")

    with pytest.raises(ValueError, match="batch_id is required."):

        jobs_client.get_job_status(study_key="STUDY123", batch_id=None)  # type: ignore
