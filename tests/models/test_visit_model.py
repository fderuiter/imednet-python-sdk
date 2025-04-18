# filepath: /Users/fred/Documents/GitHub/imednet-python-sdk/tests/models/test_visit_model.py
import pytest
from pydantic import ValidationError
from datetime import date, datetime
from typing import Optional

from imednet_sdk.models.visit import VisitModel

# Sample valid data based on docs/reference/visits.md
VALID_VISIT_DATA = {
    "visitId": 1,
    "studyKey": "PHARMADEMO",
    "intervalId": 13,
    "intervalName": "Day 15",
    "subjectId": 247,
    "subjectKey": "111-005",
    "startDate": "2024-11-04", # Optional date
    "endDate": "2024-11-11",   # Optional date
    "dueDate": None,           # Optional date (example has null)
    "visitDate": "2024-11-06", # Optional date
    "visitDateForm": "Follow Up", # Optional
    "deleted": False,          # Explicitly setting default
    "visitDateQuestion": "AESEV", # Optional
    "dateCreated": "2024-11-04 16:03:19",
    "dateModified": "2024-11-04 16:03:19"
}

def test_visit_model_validation():
    """Test successful validation of VisitModel with valid data."""
    model = VisitModel.model_validate(VALID_VISIT_DATA)

    assert model.visitId == VALID_VISIT_DATA["visitId"]
    assert model.studyKey == VALID_VISIT_DATA["studyKey"]
    assert model.intervalId == VALID_VISIT_DATA["intervalId"]
    assert model.intervalName == VALID_VISIT_DATA["intervalName"]
    assert model.subjectId == VALID_VISIT_DATA["subjectId"]
    assert model.subjectKey == VALID_VISIT_DATA["subjectKey"]
    assert isinstance(model.startDate, date)
    assert model.startDate == date(2024, 11, 4)
    assert isinstance(model.endDate, date)
    assert model.endDate == date(2024, 11, 11)
    assert model.dueDate is None
    assert isinstance(model.visitDate, date)
    assert model.visitDate == date(2024, 11, 6)
    assert model.visitDateForm == VALID_VISIT_DATA["visitDateForm"]
    assert model.deleted == VALID_VISIT_DATA["deleted"]
    assert model.visitDateQuestion == VALID_VISIT_DATA["visitDateQuestion"]
    assert isinstance(model.dateCreated, datetime)
    assert model.dateCreated == datetime(2024, 11, 4, 16, 3, 19)
    assert isinstance(model.dateModified, datetime)
    assert model.dateModified == datetime(2024, 11, 4, 16, 3, 19)

def test_visit_model_optional_fields_none_or_missing():
    """Test validation when optional fields are None or missing."""
    data_with_none = VALID_VISIT_DATA.copy()
    data_with_none["startDate"] = None
    data_with_none["endDate"] = None
    data_with_none["dueDate"] = None
    data_with_none["visitDate"] = None
    data_with_none["visitDateForm"] = None
    data_with_none["visitDateQuestion"] = None

    model_none = VisitModel.model_validate(data_with_none)
    assert model_none.startDate is None
    assert model_none.endDate is None
    assert model_none.dueDate is None
    assert model_none.visitDate is None
    assert model_none.visitDateForm is None
    assert model_none.visitDateQuestion is None

    data_missing_optionals = VALID_VISIT_DATA.copy()
    del data_missing_optionals["startDate"]
    del data_missing_optionals["endDate"]
    # dueDate is already None in base data
    del data_missing_optionals["visitDate"]
    del data_missing_optionals["visitDateForm"]
    del data_missing_optionals["visitDateQuestion"]

    model_missing = VisitModel.model_validate(data_missing_optionals)
    assert model_missing.startDate is None
    assert model_missing.endDate is None
    assert model_missing.dueDate is None
    assert model_missing.visitDate is None
    assert model_missing.visitDateForm is None
    assert model_missing.visitDateQuestion is None

def test_visit_model_defaults():
    """Test default values for boolean fields when not provided."""
    minimal_data = VALID_VISIT_DATA.copy()
    del minimal_data["deleted"]
    # Remove optional fields as well for minimal test
    del minimal_data["startDate"]
    del minimal_data["endDate"]
    minimal_data["dueDate"] = None
    del minimal_data["visitDate"]
    del minimal_data["visitDateForm"]
    del minimal_data["visitDateQuestion"]

    model = VisitModel.model_validate(minimal_data)
    assert model.deleted is False

def test_visit_model_missing_required_field():
    """Test ValidationError is raised when a required field is missing."""
    invalid_data = VALID_VISIT_DATA.copy()
    del invalid_data["intervalName"] # Remove a required field

    with pytest.raises(ValidationError) as excinfo:
        VisitModel.model_validate(invalid_data)

    assert "intervalName" in str(excinfo.value)
    assert "Field required" in str(excinfo.value)

def test_visit_model_invalid_data_type():
    """Test ValidationError is raised for incorrect data types."""
    invalid_data = VALID_VISIT_DATA.copy()
    invalid_data["visitId"] = "not-an-integer"

    with pytest.raises(ValidationError) as excinfo:
        VisitModel.model_validate(invalid_data)

    assert "visitId" in str(excinfo.value)
    assert "Input should be a valid integer" in str(excinfo.value)

    invalid_data_date = VALID_VISIT_DATA.copy()
    invalid_data_date["startDate"] = "not-a-date"
    with pytest.raises(ValidationError) as excinfo_date:
        VisitModel.model_validate(invalid_data_date)

    assert "startDate" in str(excinfo_date.value)
    assert "date" in str(excinfo_date.value).lower()

    invalid_data_datetime = VALID_VISIT_DATA.copy()
    invalid_data_datetime["dateCreated"] = "not-a-datetime"
    with pytest.raises(ValidationError) as excinfo_datetime:
        VisitModel.model_validate(invalid_data_datetime)

    assert "dateCreated" in str(excinfo_datetime.value)
    assert "datetime" in str(excinfo_datetime.value).lower()

def test_visit_model_serialization():
    """Test serialization of the VisitModel."""
    model = VisitModel.model_validate(VALID_VISIT_DATA)
    dump = model.model_dump(by_alias=True)

    expected_data = VALID_VISIT_DATA.copy()
    # Adjust date/datetime serialization if needed (Pydantic v2 defaults)
    # expected_data["startDate"] = model.startDate.isoformat()
    # expected_data["endDate"] = model.endDate.isoformat()
    # expected_data["visitDate"] = model.visitDate.isoformat()
    # expected_data["dateCreated"] = model.dateCreated.isoformat()
    # expected_data["dateModified"] = model.dateModified.isoformat()

    # Check basic fields match
    for key, value in expected_data.items():
        if key not in ["startDate", "endDate", "dueDate", "visitDate", "dateCreated", "dateModified"]:
            assert dump[key] == value

    # Check date/datetime serialization (assuming Pydantic v2 defaults)
    assert dump["startDate"] == date(2024, 11, 4)
    assert dump["endDate"] == date(2024, 11, 11)
    assert dump["dueDate"] is None
    assert dump["visitDate"] == date(2024, 11, 6)
    assert dump["dateCreated"] == datetime(2024, 11, 4, 16, 3, 19)
    assert dump["dateModified"] == datetime(2024, 11, 4, 16, 3, 19)

# Add more tests for edge cases, different date formats if custom validators are added, etc.
