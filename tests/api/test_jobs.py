# Tests for the Jobs API client.

from datetime import datetime  # Import datetime

import pytest
import respx
from httpx import Response

from imednet_sdk.client import ImednetClient
# The client method should return JobStatusModel directly based on docs
from imednet_sdk.models._common import ApiResponse
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
def test_get_job_status_success(mock_imednet_client, mock_api_response_job_status):
    """Test successful retrieval of job status."""
    study_key = "TEST_STUDY"
    batch_id = 12345
    expected_url = f"{mock_imednet_client.base_url}/studies/{study_key}/jobs/{batch_id}"
    expected_response_model = JobStatusModel(
        batchId=batch_id, state="Completed", message="Job finished successfully"
    )

    # Configure the mock client's _request method
    mock_imednet_client._request.return_value = mock_api_response_job_status(
        expected_response_model
    )

    # Call the method under test
    response = mock_imednet_client.jobs.get_job_status(study_key=study_key, batch_id=batch_id)

    # Assertions
    mock_imednet_client._request.assert_called_once_with(
        method="GET",
        endpoint=f"/studies/{study_key}/jobs/{batch_id}",
        response_model=JobStatusModel,
    )
    assert response is not None
    assert isinstance(response, ApiResponse)
    assert response.data == expected_response_model
    assert response.data.batchId == batch_id
    assert response.data.state == "Completed"


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
        "dateCreated": "2023-11-01 11:00:00",  # Use dateCreated
        "dateModified": "2023-11-01 11:00:05",  # Use dateModified
        "progress": 50,  # Example progress
        "resultUrl": None,
        "error": None,
    }
    respx.get(mock_url).mock(return_value=Response(200, json=mock_response_data))

    response = jobs_client.get_job_status(study_key=study_key, batch_id=batch_id)

    assert isinstance(response, JobStatusModel)
    assert response.batchId == batch_id
    assert response.state == "running"
    assert response.dateCreated is not None  # Check dateCreated
    assert response.dateModified is not None  # Check dateModified
    assert response.progress == 50  # Check progress
    assert response.resultUrl is None  # Check resultUrl
    assert response.error is None  # Check error


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
