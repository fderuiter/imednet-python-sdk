# filepath: /Users/fred/Documents/GitHub/imednet-python-sdk/tests/models/test_job_model.py
import pytest
from pydantic import ValidationError
from datetime import datetime
from typing import Optional

from imednet_sdk.models.job import JobStatusModel

# Sample valid data based on docs/reference/jobs.md
VALID_JOB_DATA = {
    "jobId": "afa2d61e-07ed-4efe-99c5-6f358f5e7d38",
    "batchId": "75e63db6-fa41-40bc-b939-cf3bdb246ae8",
    "state": "completed",
    "dateCreated": "2020-12-01 21:47:36",
    "dateStarted": "2020-12-01 21:47:42",
    "dateFinished": "2020-12-01 21:47:45"
}

VALID_JOB_DATA_MINIMAL = {
    "jobId": "afa2d61e-07ed-4efe-99c5-6f358f5e7d38",
    "batchId": "75e63db6-fa41-40bc-b939-cf3bdb246ae8",
    "state": "created",
    "dateCreated": "2020-12-01 21:47:36",
    # dateStarted and dateFinished are optional (None)
}

def test_job_status_model_validation_full():
    """Test successful validation of JobStatusModel with all fields."""
    model = JobStatusModel.model_validate(VALID_JOB_DATA)

    assert model.jobId == VALID_JOB_DATA["jobId"]
    assert model.batchId == VALID_JOB_DATA["batchId"]
    assert model.state == VALID_JOB_DATA["state"]
    assert isinstance(model.dateCreated, datetime)
    assert model.dateCreated == datetime(2020, 12, 1, 21, 47, 36)
    assert isinstance(model.dateStarted, datetime)
    assert model.dateStarted == datetime(2020, 12, 1, 21, 47, 42)
    assert isinstance(model.dateFinished, datetime)
    assert model.dateFinished == datetime(2020, 12, 1, 21, 47, 45)

def test_job_status_model_validation_minimal():
    """Test successful validation of JobStatusModel with only required fields."""
    model = JobStatusModel.model_validate(VALID_JOB_DATA_MINIMAL)

    assert model.jobId == VALID_JOB_DATA_MINIMAL["jobId"]
    assert model.batchId == VALID_JOB_DATA_MINIMAL["batchId"]
    assert model.state == VALID_JOB_DATA_MINIMAL["state"]
    assert isinstance(model.dateCreated, datetime)
    assert model.dateCreated == datetime(2020, 12, 1, 21, 47, 36)
    assert model.dateStarted is None
    assert model.dateFinished is None

def test_job_status_model_missing_required_field():
    """Test ValidationError is raised when a required field is missing."""
    invalid_data = VALID_JOB_DATA.copy()
    del invalid_data["jobId"] # Remove a required field

    with pytest.raises(ValidationError) as excinfo:
        JobStatusModel.model_validate(invalid_data)

    assert "jobId" in str(excinfo.value)
    assert "Field required" in str(excinfo.value)

def test_job_status_model_invalid_data_type():
    """Test ValidationError is raised for incorrect data types."""
    invalid_data = VALID_JOB_DATA.copy()
    invalid_data["dateCreated"] = "not-a-datetime"

    with pytest.raises(ValidationError) as excinfo:
        JobStatusModel.model_validate(invalid_data)

    assert "dateCreated" in str(excinfo.value)
    # Error message might vary slightly depending on Pydantic version/internals
    assert "datetime" in str(excinfo.value).lower()

def test_job_status_model_serialization_full():
    """Test serialization of the JobStatusModel with all fields."""
    model = JobStatusModel.model_validate(VALID_JOB_DATA)
    dump = model.model_dump(by_alias=True)

    expected_data = VALID_JOB_DATA.copy()
    # Adjust datetime serialization if needed

    # Check basic fields match
    for key, value in expected_data.items():
        if key not in ["dateCreated", "dateStarted", "dateFinished"]:
            assert dump[key] == value

    # Check datetime serialization
    assert dump["dateCreated"] == datetime(2020, 12, 1, 21, 47, 36)
    assert dump["dateStarted"] == datetime(2020, 12, 1, 21, 47, 42)
    assert dump["dateFinished"] == datetime(2020, 12, 1, 21, 47, 45)

def test_job_status_model_serialization_minimal():
    """Test serialization of the JobStatusModel with optional fields as None."""
    model = JobStatusModel.model_validate(VALID_JOB_DATA_MINIMAL)
    # Use exclude_none=True if you want to omit None fields during serialization
    dump = model.model_dump(by_alias=True)

    expected_data = VALID_JOB_DATA_MINIMAL.copy()
    # Add None values for optional fields if not using exclude_none
    expected_data["dateStarted"] = None
    expected_data["dateFinished"] = None

    # Check basic fields match
    for key, value in expected_data.items():
        if key not in ["dateCreated", "dateStarted", "dateFinished"]:
            assert dump[key] == value

    # Check datetime serialization
    assert dump["dateCreated"] == datetime(2020, 12, 1, 21, 47, 36)
    assert dump["dateStarted"] is None
    assert dump["dateFinished"] is None

# Add tests for different 'state' values if needed
