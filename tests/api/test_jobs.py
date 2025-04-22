# Tests for the Jobs API client.

import datetime

import pytest
import respx
from httpx import Response

from imednet_sdk.client import ImednetClient
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
def test_get_job_status_success(client):  # Removed mock_api_response_job_status fixture
    """Test successful retrieval of job status, aligned with documentation."""
    study_key = "TEST_STUDY"
    batch_id = "1601b8a0-45ba-4136-8c55-17fab704bc80"  # Use string batchId as per docs example
    # Construct the full expected URL based on documentation path structure
    expected_url = f"{client.base_url}/api/v1/edc/studies/{study_key}/jobs/{batch_id}"

    # Define the mock JSON response data based on documentation fields and format
    mock_response_data = {
        "jobId": "afa2d61e-07ed-4efe-99c5-6f358f5e7d38",  # Example from docs
        "batchId": batch_id,
        "state": "completed",  # Lowercase as per docs
        # Use YYYY-MM-DD HH:MM:SS format as per docs
        "dateCreated": "2020-12-01 21:47:36",
        "dateStarted": "2020-12-01 21:47:42",  # Added field from docs
        "dateFinished": "2020-12-01 21:47:45",  # Added field from docs
        # Removed fields not in docs: message, dateModified, progress, resultUrl, error
    }

    # Define the expected JobStatusModel instance based on the mock data
    # Assuming JobStatusModel can parse the documented date format string
    # If JobStatusModel expects datetime objects, parsing is needed here.
    # For simplicity, let's assume the model handles string dates for now,
    # but this might need adjustment based on the model's implementation.
    expected_response_model = JobStatusModel(
        jobId="afa2d61e-07ed-4efe-99c5-6f358f5e7d38",
        batchId=batch_id,
        state="completed",
        dateCreated="2020-12-01 21:47:36",  # Pass string directly
        dateStarted="2020-12-01 21:47:42",  # Pass string directly
        dateFinished="2020-12-01 21:47:45",  # Pass string directly
        # Removed fields not in docs
    )

    # Mock the specific GET request using respx with the correct URL
    route = respx.get(expected_url).mock(return_value=Response(200, json=mock_response_data))

    # Call the method under test
    # Assuming client.jobs.get_job_status internally calls the correct endpoint path
    response = client.jobs.get_job_status(study_key=study_key, batch_id=batch_id)

    # Assertions
    assert route.called, f"Expected call to {expected_url} was not made."
    assert isinstance(response, JobStatusModel)  # Check for JobStatusModel instance

    # Compare model instances - This assumes JobStatusModel correctly parses/stores the data
    # Direct comparison might fail if date strings aren't parsed into comparable types (like datetime)
    # within the model. Adjust assertion if needed.
    assert response.jobId == expected_response_model.jobId
    assert response.batchId == expected_response_model.batchId
    assert response.state == expected_response_model.state
    # Assuming the model stores dates as strings for this test based on input
    assert str(response.dateCreated) == expected_response_model.dateCreated
    assert str(response.dateStarted) == expected_response_model.dateStarted
    assert str(response.dateFinished) == expected_response_model.dateFinished
    # assert response == expected_response_model # Use field-by-field if direct compare fails


@respx.mock
def test_get_job_status_running(jobs_client, client):  # Renamed for clarity
    """Test retrieval of job status when running."""
    study_key = "STUDYBATCH"
    batch_id = "BATCHRUNNING"  # Keep as string
    # Correct the mock URL path
    mock_url = f"{client.base_url}/api/v1/edc/studies/{study_key}/jobs/{batch_id}"
    # Mock response for a 'running' state based on docs structure
    mock_response_data = {
        "jobId": "JOBRUN1",
        "batchId": batch_id,
        "state": "running",  # Lowercase as per docs
        "dateCreated": "2023-11-01 11:00:00",  # Use documented format
        "dateStarted": "2023-11-01 11:00:05",  # Use documented format (assuming dateStarted is relevant here)
        "dateFinished": None,  # Job is running, so not finished
        # Removed fields not in docs: progress, resultUrl, error, dateModified
    }
    respx.get(mock_url).mock(return_value=Response(200, json=mock_response_data))

    response = jobs_client.get_job_status(study_key=study_key, batch_id=batch_id)

    assert isinstance(response, JobStatusModel)
    assert response.batchId == batch_id
    assert response.state == "running"
    # Assuming model stores dates as strings or parses them correctly
    assert str(response.dateCreated) == "2023-11-01 11:00:00"  # Check dateCreated string
    assert str(response.dateStarted) == "2023-11-01 11:00:05"  # Check dateStarted string
    assert response.dateFinished is None  # Check dateFinished
    # Removed assertions for fields not in docs


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
