"""Tests for study-related models."""

from datetime import datetime
from typing import List, Optional

import pytest
from pydantic import TypeAdapter, ValidationError

from imednet_sdk.models._common import ApiResponse, Metadata
from imednet_sdk.models.study import StudyModel

# Sample valid data based on docs/reference/studies.md
VALID_STUDY_DATA = {
    "sponsorKey": "100",
    "studyKey": "PHARMADEMO",
    "studyId": 100,
    "studyName": "iMednet Pharma Demonstration Study",
    "studyDescription": "iMednet Demonstration Study v2 Created 05April2018 After A5 Release",  # Optional
    "studyType": "STUDY",
    "dateCreated": "2024-11-04 16:03:18",
    "dateModified": "2024-11-04 16:03:19",
}


def test_study_model_validation():
    """Test successful validation of StudyModel with valid data."""
    model = StudyModel.model_validate(VALID_STUDY_DATA)

    assert model.sponsorKey == VALID_STUDY_DATA["sponsorKey"]
    assert model.studyKey == VALID_STUDY_DATA["studyKey"]
    assert model.studyId == VALID_STUDY_DATA["studyId"]
    assert model.studyName == VALID_STUDY_DATA["studyName"]
    assert model.studyDescription == VALID_STUDY_DATA["studyDescription"]
    assert model.studyType == VALID_STUDY_DATA["studyType"]
    assert isinstance(model.dateCreated, datetime)
    assert model.dateCreated == datetime(2024, 11, 4, 16, 3, 18)
    assert isinstance(model.dateModified, datetime)
    assert model.dateModified == datetime(2024, 11, 4, 16, 3, 19)


def test_study_model_optional_fields_none_or_missing():
    """Test validation when optional fields are None or missing."""
    data_with_none = VALID_STUDY_DATA.copy()
    data_with_none["studyDescription"] = None

    model_none = StudyModel.model_validate(data_with_none)
    assert model_none.studyDescription is None

    data_missing_optionals = VALID_STUDY_DATA.copy()
    del data_missing_optionals["studyDescription"]

    model_missing = StudyModel.model_validate(data_missing_optionals)
    assert model_missing.studyDescription is None  # Should default to None


def test_study_model_missing_required_field():
    """Test ValidationError is raised when a required field is missing."""
    invalid_data = VALID_STUDY_DATA.copy()
    del invalid_data["studyName"]  # Remove a required field

    with pytest.raises(ValidationError) as excinfo:
        StudyModel.model_validate(invalid_data)

    assert "studyName" in str(excinfo.value)
    assert "Field required" in str(excinfo.value)


def test_study_model_invalid_data_type():
    """Test ValidationError is raised for incorrect data types."""
    invalid_data = VALID_STUDY_DATA.copy()
    invalid_data["studyId"] = "not-an-integer"

    with pytest.raises(ValidationError) as excinfo:
        StudyModel.model_validate(invalid_data)

    assert "studyId" in str(excinfo.value)
    assert "Input should be a valid integer" in str(excinfo.value)

    invalid_data_datetime = VALID_STUDY_DATA.copy()
    invalid_data_datetime["dateCreated"] = "not-a-datetime"
    with pytest.raises(ValidationError) as excinfo_datetime:
        StudyModel.model_validate(invalid_data_datetime)

    assert "dateCreated" in str(excinfo_datetime.value)
    assert "datetime" in str(excinfo_datetime.value).lower()


def test_study_model_serialization():
    """Test serialization of the StudyModel."""
    model = StudyModel.model_validate(VALID_STUDY_DATA)
    dump = model.model_dump(by_alias=True)

    expected_data = VALID_STUDY_DATA.copy()
    # Adjust datetime serialization if needed

    # Check basic fields match
    for key, value in expected_data.items():
        if key not in ["dateCreated", "dateModified"]:
            assert dump[key] == value

    # Check datetime serialization
    assert dump["dateCreated"] == datetime(2024, 11, 4, 16, 3, 18)
    assert dump["dateModified"] == datetime(2024, 11, 4, 16, 3, 19)


def test_study_optional_fields():
    """Test handling of optional fields."""
    study_data = {
        "sponsorKey": "100",
        "studyKey": "PHARMADEMO",
        "studyId": 100,
        "studyName": "Test Study",
        "studyType": "STUDY",
        "dateCreated": "2024-11-04 16:03:18",
        "dateModified": "2024-11-04 16:03:19",
        "studyDescription": None,  # Optional field set to null
    }
    study = StudyModel.model_validate(study_data)
    assert study.studyDescription is None


def test_study_list_validation():
    """Test validation of a list of studies using TypeAdapter."""
    studies_data = [
        {
            "sponsorKey": "100",
            "studyKey": "STUDY1",
            "studyId": 100,
            "studyName": "Study 1",
            "studyType": "STUDY",
            "dateCreated": "2024-11-04 16:03:18",
            "dateModified": "2024-11-04 16:03:19",
        },
        {
            "sponsorKey": "100",
            "studyKey": "STUDY2",
            "studyId": 101,
            "studyName": "Study 2",
            "studyType": "STUDY",
            "dateCreated": "2024-11-04 16:03:18",
            "dateModified": "2024-11-04 16:03:19",
        },
    ]

    type_adapter = TypeAdapter(List[StudyModel])
    studies = type_adapter.validate_python(studies_data)
    assert len(studies) == 2
    assert all(isinstance(study, StudyModel) for study in studies)


def test_study_api_response():
    """Test StudyModel within ApiResponse."""
    response_data = {
        "metadata": {"status": "OK", "timestamp": "2024-11-04 16:03:18"},
        "data": {
            "sponsorKey": "100",
            "studyKey": "PHARMADEMO",
            "studyId": 100,
            "studyName": "Test Study",
            "studyType": "STUDY",
            "dateCreated": "2024-11-04 16:03:18",
            "dateModified": "2024-11-04 16:03:19",
        },
    }

    response = ApiResponse[StudyModel].model_validate(response_data)
    assert isinstance(response.data, StudyModel)
    assert response.data.studyKey == "PHARMADEMO"
