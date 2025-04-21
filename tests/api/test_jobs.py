# Tests for the Jobs API client.

import pytest
import respx
from httpx import Response

from imednet_sdk.client import ImednetClient
from imednet_sdk.models._common import ApiResponse
from imednet_sdk.models.job import JobStatusModel


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

    study_key = "STUDYBATCH"
    batch_id = "BATCH12345"
    mock_url = f"{client.base_url}/api/v1/edc/studies/{study_key}/jobs/{batch_id}"
    mock_response_data = {
        "jobId": "JOB987",
        "batchId": batch_id,
        "state": "Completed",
        "message": "Record creation completed successfully.",
        "submitted": "2023-11-01T10:00:00Z",
        "started": "2023-11-01T10:00:05Z",
        "completed": "2023-11-01T10:05:00Z",
        "totalRecords": 100,
        "processedRecords": 100,
        "failedRecords": 0,
        "errorDetails": [],
    }
    # Note: Job status endpoint might not return metadata, adjust if needed based on API spec
    mock_metadata = {"page": 1, "size": 1, "totalRecords": 1, "totalPages": 1}  # Placeholder
    mock_response = {"metadata": mock_metadata, "data": mock_response_data}

    respx.get(mock_url).mock(return_value=Response(200, json=mock_response))

    response = jobs_client.get_job_status(study_key=study_key, batch_id=batch_id)

    assert isinstance(response, ApiResponse)
    # assert isinstance(response.metadata, Metadata) # Adjust based on actual API response
    assert isinstance(response.data, JobStatusModel)
    assert response.data.batchId == batch_id
    assert response.data.state == "Completed"
    assert response.data.totalRecords == 100


@respx.mock
def test_get_job_status_pending(jobs_client, client):
    """Test retrieval of job status when pending."""

    study_key = "STUDYBATCH"
    batch_id = "BATCHPENDING"
    mock_url = f"{client.base_url}/api/v1/edc/studies/{study_key}/jobs/{batch_id}"
    mock_response_data = {
        "jobId": "JOB654",
        "batchId": batch_id,
        "state": "Pending",
        "message": "Job is waiting to be processed.",
        "submitted": "2023-11-01T11:00:00Z",
        "started": None,
        "completed": None,
        "totalRecords": 50,
        "processedRecords": 0,
        "failedRecords": 0,
        "errorDetails": [],
    }
    mock_metadata = {"page": 1, "size": 1, "totalRecords": 1, "totalPages": 1}  # Placeholder
    mock_response = {"metadata": mock_metadata, "data": mock_response_data}

    respx.get(mock_url).mock(return_value=Response(200, json=mock_response))

    response = jobs_client.get_job_status(study_key=study_key, batch_id=batch_id)

    assert isinstance(response, ApiResponse)
    assert isinstance(response.data, JobStatusModel)
    assert response.data.batchId == batch_id
    assert response.data.state == "Pending"
    assert response.data.started is None
    assert response.data.completed is None


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
