"""Tests for study-related models."""

from datetime import datetime
from typing import List

import pytest
from pydantic import TypeAdapter, ValidationError

from imednet_sdk.models._common import ApiResponse, Metadata
from imednet_sdk.models.study import StudyModel


def test_study_model_validation():
    """Test successful validation of StudyModel."""
    study_data = {
        "sponsorKey": "100",
        "studyKey": "PHARMADEMO",
        "studyId": 100,
        "studyName": "iMednet Pharma Demonstration Study",
        "studyDescription": "iMednet Demonstration Study v2",
        "studyType": "STUDY",
        "dateCreated": "2024-11-04 16:03:18",
        "dateModified": "2024-11-04 16:03:19",
    }
    study = StudyModel.model_validate(study_data)
    assert study.sponsorKey == "100"
    assert study.studyKey == "PHARMADEMO"
    assert study.studyName == "iMednet Pharma Demonstration Study"


def test_study_serialization():
    """Test serialization of StudyModel to JSON/dict."""
    study = StudyModel(
        sponsorKey="100",
        studyKey="PHARMADEMO",
        studyId=100,
        studyName="Test Study",
        studyType="STUDY",
        dateCreated=datetime.now(),
        dateModified=datetime.now(),
    )
    # Test dict serialization
    data_dict = study.model_dump()
    assert isinstance(data_dict, dict)
    assert data_dict["sponsorKey"] == "100"

    # Test JSON serialization
    json_data = study.model_dump(mode="json")
    assert isinstance(json_data, dict)
    assert json_data["studyKey"] == "PHARMADEMO"


def test_study_missing_required():
    """Test ValidationError is raised for missing required fields."""
    invalid_data = {
        "studyKey": "PHARMADEMO",  # Missing other required fields
    }
    with pytest.raises(ValidationError):
        StudyModel.model_validate(invalid_data)


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
