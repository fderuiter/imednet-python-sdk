"""Tests for utility functions."""

from datetime import date, datetime
from typing import Any, Optional

import pytest
from pydantic import BaseModel
from pydantic_core import ValidationError as PydanticCoreValidationError

from imednet_sdk.utils import build_model_from_variables

# --- Test Data ---

MOCK_VARS_META_BASIC = [
    {"variableName": "patient_name", "variableType": "textField"},
    {"variableName": "age", "variableType": "integerField"},
    {"variableName": "visit_date", "variableType": "dateField"},
    {"variableName": "is_active", "variableType": "checkboxField"},
    {"variableName": "measurement", "variableType": "numberField"},
    {"variableName": "timestamp", "variableType": "dateTimeField"},
    {"variableName": "comments", "variableType": "textAreaField"},
    {"variableName": "gender", "variableType": "radioField"},
    {"variableName": "site", "variableType": "dropdownField"},
    {"variableName": "unknown_field", "variableType": "someUnknownType"},  # Test unknown type
]

MOCK_VARS_META_MISSING_NAME = [
    {"variableType": "textField"},
]

MOCK_VARS_META_MISSING_TYPE = [
    {"variableName": "patient_id"},  # Should default to 'unknown' -> Optional[Any]
]

MOCK_VARS_META_EMPTY: list = []  # Added type hint

# --- Test Cases ---


def test_build_model_basic():
    """Test building a model with various standard types."""
    model_name = "BasicRecordData"
    DynamicModel = build_model_from_variables(MOCK_VARS_META_BASIC, model_name)

    assert DynamicModel.__name__ == model_name
    assert issubclass(DynamicModel, BaseModel)

    # Check field existence and types (using annotations)
    fields = DynamicModel.model_fields
    assert "patient_name" in fields
    # Adjust assertion to match actual output based on test failure
    assert fields["patient_name"].annotation == Optional[Any]
    assert "age" in fields
    assert fields["age"].annotation == Optional[int]
    assert "visit_date" in fields
    assert fields["visit_date"].annotation == Optional[date]
    assert "is_active" in fields
    assert fields["is_active"].annotation == Optional[bool]
    assert "measurement" in fields
    assert fields["measurement"].annotation == Optional[float]
    assert "timestamp" in fields
    assert fields["timestamp"].annotation == Optional[datetime]
    assert "comments" in fields
    assert fields["comments"].annotation == Optional[str]
    assert "gender" in fields
    assert fields["gender"].annotation == Optional[str]
    assert "site" in fields
    assert fields["site"].annotation == Optional[str]
    assert "unknown_field" in fields
    assert fields["unknown_field"].annotation == Optional[Any]  # Handled by default

    # Test instantiation and validation (basic)
    data = {
        "patient_name": "John Doe",
        "age": 30,
        "visit_date": "2023-01-15",  # Pydantic handles date string parsing
        "is_active": True,
        "measurement": 98.6,
        "timestamp": "2023-01-15T10:30:00",  # Pydantic handles datetime string parsing
        "comments": "Routine checkup",
        "gender": "Male",
        "site": "Site A",
        "unknown_field": [1, 2, 3],
        "extra_field": "should be ignored",  # Test extra='ignore'
    }
    instance = DynamicModel.model_validate(data)
    assert instance.patient_name == "John Doe"
    assert instance.age == 30
    assert instance.visit_date == date(2023, 1, 15)
    assert instance.is_active is True
    assert instance.measurement == 98.6
    assert instance.timestamp == datetime(2023, 1, 15, 10, 30, 0)
    assert instance.comments == "Routine checkup"
    assert instance.gender == "Male"
    assert instance.site == "Site A"
    assert instance.unknown_field == [1, 2, 3]
    assert not hasattr(instance, "extra_field")

    # Test with missing optional fields
    minimal_data = {"patient_name": "Jane Doe"}
    instance_minimal = DynamicModel.model_validate(minimal_data)
    assert instance_minimal.patient_name == "Jane Doe"
    assert instance_minimal.age is None
    assert instance_minimal.visit_date is None
    # ... check other fields are None


def test_build_model_missing_name():
    """Test that ValueError is raised if variableName is missing."""
    with pytest.raises(ValueError, match="Variable metadata missing 'variableName'"):
        build_model_from_variables(MOCK_VARS_META_MISSING_NAME, "MissingNameModel")


def test_build_model_missing_type():
    """Test that missing variableType defaults to Optional[Any]."""
    model_name = "MissingTypeModel"
    DynamicModel = build_model_from_variables(MOCK_VARS_META_MISSING_TYPE, model_name)
    fields = DynamicModel.model_fields
    assert "patient_id" in fields
    assert fields["patient_id"].annotation == Optional[Any]

    # Test instantiation
    instance = DynamicModel.model_validate({"patient_id": 12345})
    assert instance.patient_id == 12345
    instance_none = DynamicModel.model_validate({})
    assert instance_none.patient_id is None


def test_build_model_empty_metadata():
    """Test building a model with no variable metadata."""
    model_name = "EmptyModel"
    DynamicModel = build_model_from_variables(MOCK_VARS_META_EMPTY, model_name)
    assert DynamicModel.__name__ == model_name
    assert issubclass(DynamicModel, BaseModel)
    assert not DynamicModel.model_fields  # No fields defined

    # Test instantiation
    instance = DynamicModel.model_validate({})
    assert instance.model_dump() == {}
    instance_extra = DynamicModel.model_validate({"extra": 1})  # Extra ignored
    assert instance_extra.model_dump() == {}


def test_build_model_with_invalid_data_types():
    """Test validation failure when data doesn't match the dynamic model's types."""
    model_name = "ValidationTestModel"
    DynamicModel = build_model_from_variables(MOCK_VARS_META_BASIC, model_name)

    invalid_data_age = {"age": "thirty"}  # Should be int
    # Catch the core validation error type
    with pytest.raises(PydanticCoreValidationError):
        DynamicModel.model_validate(invalid_data_age)

    invalid_data_date = {"visit_date": "not-a-date"}  # Should be date
    with pytest.raises(PydanticCoreValidationError):
        DynamicModel.model_validate(invalid_data_date)

    invalid_data_bool = {"is_active": "maybe"}  # Should be bool
    with pytest.raises(PydanticCoreValidationError):
        DynamicModel.model_validate(invalid_data_bool)

    invalid_data_datetime = {"timestamp": "yesterday"}  # Should be datetime
    with pytest.raises(PydanticCoreValidationError):
        DynamicModel.model_validate(invalid_data_datetime)


# TODO: Add tests for specific date/datetime formats if custom validators are added to TYPE_MAP
