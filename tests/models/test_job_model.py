from imednet_sdk.models._common import ErrorDetail
from imednet_sdk.models.job import JobStatusModel

import pytest
from datetime import datetime
from pydantic import ValidationError

# Mock data based on docs/reference/jobs.md examples
VALID_JOB_DATA = {
    "jobId": "afa2d61e-07ed-4efe-99c5-6f358f5e7d38",
    "batchId": "75e63db6-fa41-40bc-b939-cf3bdb246ae8",
    "state": "completed",
    "dateCreated": "2020-12-01 21:47:36",
    "dateModified": "2020-12-01 21:47:42", # Use dateModified
    "progress": 100,
    "resultUrl": "/api/v1/edc/jobs/afa2d61e-07ed-4efe-99c5-6f358f5e7d38/results",
    "error": None,
}

VALID_JOB_DATA_MINIMAL = {
    "jobId": "afa2d61e-07ed-4efe-99c5-6f358f5e7d38",
    "batchId": "75e63db6-fa41-40bc-b939-cf3bdb246ae8", # batchId is optional in model, but often present
    "state": "created",
    "dateCreated": "2020-12-01 21:47:36",
    # Optional fields omitted
}

INVALID_JOB_DATA_MISSING_REQUIRED = {
    "batchId": "75e63db6-fa41-40bc-b939-cf3bdb246ae8",
    "state": "created",
    "dateCreated": "2020-12-01 21:47:36",
}

INVALID_JOB_DATA_WRONG_TYPE = {
    "jobId": "afa2d61e-07ed-4efe-99c5-6f358f5e7d38",
    "batchId": "75e63db6-fa41-40bc-b939-cf3bdb246ae8",
    "state": "created",
    "dateCreated": "not-a-date", # Invalid date format
}


def test_job_status_model_validation_full():
    """Test successful validation of JobStatusModel with all fields."""
    model = JobStatusModel.model_validate(VALID_JOB_DATA)

    assert model.jobId == VALID_JOB_DATA["jobId"]
    assert model.batchId == VALID_JOB_DATA["batchId"]
    assert model.state == VALID_JOB_DATA["state"]
    assert isinstance(model.dateCreated, datetime)
    assert model.dateCreated == datetime(2020, 12, 1, 21, 47, 36)
    assert isinstance(model.dateModified, datetime) # Check dateModified
    assert model.dateModified == datetime(2020, 12, 1, 21, 47, 42) # Check dateModified value
    assert model.progress == 100
    assert model.resultUrl == VALID_JOB_DATA["resultUrl"]
    assert model.error is None


def test_job_status_model_validation_minimal():
    """Test successful validation of JobStatusModel with only required fields."""
    model = JobStatusModel.model_validate(VALID_JOB_DATA_MINIMAL)

    assert model.jobId == VALID_JOB_DATA_MINIMAL["jobId"]
    assert model.batchId == VALID_JOB_DATA_MINIMAL["batchId"]
    assert model.state == VALID_JOB_DATA_MINIMAL["state"]
    assert isinstance(model.dateCreated, datetime)
    assert model.dateCreated == datetime(2020, 12, 1, 21, 47, 36)
    assert model.dateModified is None # Check optional fields are None
    assert model.progress is None
    assert model.resultUrl is None
    assert model.error is None


def test_job_status_model_validation_missing_required():
    """Test validation failure when required fields are missing."""
    with pytest.raises(ValidationError) as excinfo:
        JobStatusModel.model_validate(INVALID_JOB_DATA_MISSING_REQUIRED)
    # Check that the error is about the missing 'jobId' field
    assert "jobId" in str(excinfo.value)
    assert "Field required" in str(excinfo.value)


def test_job_status_model_validation_wrong_type():
    """Test validation failure when fields have incorrect types."""
    with pytest.raises(ValidationError) as excinfo:
        JobStatusModel.model_validate(INVALID_JOB_DATA_WRONG_TYPE)
    # Check that the error is about the invalid 'dateCreated' format
    assert "dateCreated" in str(excinfo.value)
    assert "Input should be a valid datetime" in str(excinfo.value)


def test_job_status_model_serialization_full():
    """Test serialization of the JobStatusModel with all fields."""
    model = JobStatusModel.model_validate(VALID_JOB_DATA)
    dump = model.model_dump(mode="json") # Use mode='json' for datetime serialization

    expected_data = VALID_JOB_DATA.copy()
    # Pydantic v2 serializes datetimes to ISO format strings by default with mode='json'
    expected_data["dateCreated"] = "2020-12-01T21:47:36"
    expected_data["dateModified"] = "2020-12-01T21:47:42"

    # Check all fields match the expected serialized format
    assert dump["jobId"] == expected_data["jobId"]
    assert dump["batchId"] == expected_data["batchId"]
    assert dump["state"] == expected_data["state"]
    assert dump["dateCreated"] == expected_data["dateCreated"]
    assert dump["dateModified"] == expected_data["dateModified"]
    assert dump["progress"] == expected_data["progress"]
    assert dump["resultUrl"] == expected_data["resultUrl"]
    assert dump["error"] == expected_data["error"] # Should be None


def test_job_status_model_serialization_minimal():
    """Test serialization of the JobStatusModel with optional fields as None."""
    model = JobStatusModel.model_validate(VALID_JOB_DATA_MINIMAL)
    # Use exclude_none=True if you want to omit None fields during serialization
    dump = model.model_dump(mode="json", exclude_none=True)

    expected_data = {
        "jobId": VALID_JOB_DATA_MINIMAL["jobId"],
        "batchId": VALID_JOB_DATA_MINIMAL["batchId"],
        "state": VALID_JOB_DATA_MINIMAL["state"],
        "dateCreated": "2020-12-01T21:47:36", # Serialized datetime
    }

    # Check that only non-None fields are present and match
    assert dump == expected_data


def test_job_status_model_with_error():
    """Test JobStatusModel with an error field."""
    error_data = {
        "jobId": "job123",
        "state": "failed",
        "dateCreated": "2023-01-01 10:00:00",
        "error": {"code": "E001", "message": "Processing failed"}
    }
    model = JobStatusModel.model_validate(error_data)
    assert isinstance(model.error, ErrorDetail)
    assert model.error.code == "E001"
    assert model.error.description == "Processing failed" # Use description field

    dump = model.model_dump(mode="json", exclude_none=True)
    assert dump["error"]["code"] == "E001"
    assert dump["error"]["description"] == "Processing failed" # Use description field
