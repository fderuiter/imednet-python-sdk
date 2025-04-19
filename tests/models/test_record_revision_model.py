from datetime import datetime

import pytest
from pydantic import ValidationError

from imednet_sdk.models.record_revision import RecordRevisionModel

# Sample valid data based on docs/reference/record_revisions.md
VALID_RECORD_REVISION_DATA = {
    "studyKey": "PHARMADEMO",
    "recordRevisionId": 1,
    "recordId": 1,
    "recordOid": "REC-1",
    "recordRevision": 1,
    "dataRevision": 1,
    "recordStatus": "Record Complete",
    "subjectId": 247,
    "subjectOid": "OID-1",
    "subjectKey": "001-003",
    "siteId": 2,
    "formKey": "AE",
    "intervalId": 15,
    "role": "Research Coordinator",
    "user": "jdoe",
    "reasonForChange": "Data entry error",  # Optional
    "deleted": True,  # Example has true, model default is false
    "dateCreated": "2024-11-04 16:03:19",
}


def test_record_revision_model_validation():
    """Test successful validation of RecordRevisionModel with valid data."""
    model = RecordRevisionModel.model_validate(VALID_RECORD_REVISION_DATA)

    assert model.studyKey == VALID_RECORD_REVISION_DATA["studyKey"]
    assert model.recordRevisionId == VALID_RECORD_REVISION_DATA["recordRevisionId"]
    assert model.recordId == VALID_RECORD_REVISION_DATA["recordId"]
    assert model.recordOid == VALID_RECORD_REVISION_DATA["recordOid"]
    assert model.recordRevision == VALID_RECORD_REVISION_DATA["recordRevision"]
    assert model.dataRevision == VALID_RECORD_REVISION_DATA["dataRevision"]
    assert model.recordStatus == VALID_RECORD_REVISION_DATA["recordStatus"]
    assert model.subjectId == VALID_RECORD_REVISION_DATA["subjectId"]
    assert model.subjectOid == VALID_RECORD_REVISION_DATA["subjectOid"]
    assert model.subjectKey == VALID_RECORD_REVISION_DATA["subjectKey"]
    assert model.siteId == VALID_RECORD_REVISION_DATA["siteId"]
    assert model.formKey == VALID_RECORD_REVISION_DATA["formKey"]
    assert model.intervalId == VALID_RECORD_REVISION_DATA["intervalId"]
    assert model.role == VALID_RECORD_REVISION_DATA["role"]
    assert model.user == VALID_RECORD_REVISION_DATA["user"]
    assert model.reasonForChange == VALID_RECORD_REVISION_DATA["reasonForChange"]
    assert model.deleted == VALID_RECORD_REVISION_DATA["deleted"]
    assert isinstance(model.dateCreated, datetime)
    assert model.dateCreated == datetime(2024, 11, 4, 16, 3, 19)


def test_record_revision_model_optional_fields_none():
    """Test validation when optional fields are explicitly None or missing."""
    data_with_none = VALID_RECORD_REVISION_DATA.copy()
    data_with_none["reasonForChange"] = None

    model = RecordRevisionModel.model_validate(data_with_none)
    assert model.reasonForChange is None

    data_missing_optionals = VALID_RECORD_REVISION_DATA.copy()
    del data_missing_optionals["reasonForChange"]
    model_missing = RecordRevisionModel.model_validate(data_missing_optionals)
    assert model_missing.reasonForChange is None  # Should default to None


def test_record_revision_model_missing_required_field():
    """Test ValidationError is raised when a required field is missing."""
    invalid_data = VALID_RECORD_REVISION_DATA.copy()
    del invalid_data["recordId"]  # Remove a required field

    with pytest.raises(ValidationError) as excinfo:
        RecordRevisionModel.model_validate(invalid_data)

    assert "recordId" in str(excinfo.value)
    assert "Field required" in str(excinfo.value)


def test_record_revision_model_invalid_data_type():
    """Test ValidationError is raised for incorrect data types."""
    invalid_data = VALID_RECORD_REVISION_DATA.copy()
    invalid_data["recordRevisionId"] = "not-an-integer"

    with pytest.raises(ValidationError) as excinfo:
        RecordRevisionModel.model_validate(invalid_data)

    assert "recordRevisionId" in str(excinfo.value)
    assert "Input should be a valid integer" in str(excinfo.value)

    invalid_data_bool = VALID_RECORD_REVISION_DATA.copy()
    invalid_data_bool["deleted"] = "not-a-boolean"
    with pytest.raises(ValidationError) as excinfo_bool:
        RecordRevisionModel.model_validate(invalid_data_bool)

    assert "deleted" in str(excinfo_bool.value)
    assert "Input should be a valid boolean" in str(excinfo_bool.value)


def test_record_revision_model_serialization():
    """Test serialization of the RecordRevisionModel."""
    model = RecordRevisionModel.model_validate(VALID_RECORD_REVISION_DATA)
    dump = model.model_dump(by_alias=True)

    expected_data = VALID_RECORD_REVISION_DATA.copy()
    # Adjust datetime serialization if needed

    # Check basic fields match
    for key, value in expected_data.items():
        if key != "dateCreated":
            assert dump[key] == value

    # Check datetime serialization
    assert dump["dateCreated"] == datetime(2024, 11, 4, 16, 3, 19)


# Add more tests for edge cases, default values, etc.
