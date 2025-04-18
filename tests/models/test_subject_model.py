"""Tests for subject-related models."""

from datetime import datetime
from typing import List

import pytest
from pydantic import TypeAdapter, ValidationError

from imednet_sdk.models._common import ApiResponse, Metadata
from imednet_sdk.models.subject import KeywordModel, SubjectModel


def test_keyword_model():
    """Test KeywordModel validation and serialization."""
    keyword_data = {
        "keywordName": "Data Entry Error",
        "keywordKey": "DEE",
        "keywordId": 15362,
        "dateAdded": "2024-11-04 16:03:19",
    }
    keyword = KeywordModel.model_validate(keyword_data)
    assert keyword.keywordName == "Data Entry Error"
    assert keyword.keywordKey == "DEE"


def test_subject_model_validation():
    """Test successful validation of SubjectModel."""
    subject_data = {
        "studyKey": "PHARMADEMO",
        "subjectId": 1,
        "subjectOid": "OID-1",
        "subjectKey": "01-001",
        "subjectStatus": "Enrolled",
        "siteId": 128,
        "siteName": "Chicago Hope Hospital",
        "enrollmentStartDate": "2024-11-04 16:03:19",
        "dateCreated": "2024-11-04 16:03:19",
        "dateModified": "2024-11-04 16:03:20",
        "keywords": [
            {
                "keywordName": "Data Entry Error",
                "keywordKey": "DEE",
                "keywordId": 15362,
                "dateAdded": "2024-11-04 16:03:19",
            }
        ],
    }
    subject = SubjectModel.model_validate(subject_data)
    assert subject.subjectId == 1
    assert subject.subjectStatus == "Enrolled"
    assert len(subject.keywords) == 1
    assert isinstance(subject.keywords[0], KeywordModel)


def test_subject_serialization():
    """Test serialization of SubjectModel to JSON/dict."""
    subject = SubjectModel(
        studyKey="PHARMADEMO",
        subjectId=1,
        subjectOid="OID-1",
        subjectKey="01-001",
        subjectStatus="Enrolled",
        siteId=128,
        siteName="Test Site",
        enrollmentStartDate=datetime.now(),
        dateCreated=datetime.now(),
        dateModified=datetime.now(),
        keywords=[
            KeywordModel(
                keywordName="Test Keyword", keywordKey="TK", keywordId=1, dateAdded=datetime.now()
            )
        ],
    )
    # Test dict serialization
    data_dict = subject.model_dump()
    assert isinstance(data_dict, dict)
    assert data_dict["subjectKey"] == "01-001"
    assert len(data_dict["keywords"]) == 1

    # Test JSON serialization
    json_data = subject.model_dump(mode="json")
    assert isinstance(json_data, dict)
    assert json_data["subjectStatus"] == "Enrolled"


def test_subject_missing_required():
    """Test ValidationError is raised for missing required fields."""
    invalid_data = {
        "subjectId": 1,  # Missing other required fields
    }
    with pytest.raises(ValidationError):
        SubjectModel.model_validate(invalid_data)


def test_subject_optional_keywords():
    """Test handling of optional keywords field."""
    subject_data = {
        "studyKey": "PHARMADEMO",
        "subjectId": 1,
        "subjectOid": "OID-1",
        "subjectKey": "01-001",
        "subjectStatus": "Enrolled",
        "siteId": 128,
        "siteName": "Test Site",
        "enrollmentStartDate": "2024-11-04 16:03:19",
        "dateCreated": "2024-11-04 16:03:19",
        "dateModified": "2024-11-04 16:03:20",
        # No keywords field
    }
    subject = SubjectModel.model_validate(subject_data)
    assert subject.keywords is None


def test_subject_list_validation():
    """Test validation of a list of subjects using TypeAdapter."""
    subjects_data = [
        {
            "studyKey": "PHARMADEMO",
            "subjectId": 1,
            "subjectOid": "OID-1",
            "subjectKey": "01-001",
            "subjectStatus": "Enrolled",
            "siteId": 128,
            "siteName": "Test Site",
            "enrollmentStartDate": "2024-11-04 16:03:19",
            "dateCreated": "2024-11-04 16:03:19",
            "dateModified": "2024-11-04 16:03:20",
        },
        {
            "studyKey": "PHARMADEMO",
            "subjectId": 2,
            "subjectOid": "OID-2",
            "subjectKey": "01-002",
            "subjectStatus": "Enrolled",
            "siteId": 128,
            "siteName": "Test Site",
            "enrollmentStartDate": "2024-11-04 16:03:19",
            "dateCreated": "2024-11-04 16:03:19",
            "dateModified": "2024-11-04 16:03:20",
        },
    ]

    type_adapter = TypeAdapter(List[SubjectModel])
    subjects = type_adapter.validate_python(subjects_data)
    assert len(subjects) == 2
    assert all(isinstance(subject, SubjectModel) for subject in subjects)


def test_subject_api_response():
    """Test SubjectModel within ApiResponse."""
    response_data = {
        "metadata": {"status": "OK", "timestamp": "2024-11-04 16:03:19"},
        "data": {
            "studyKey": "PHARMADEMO",
            "subjectId": 1,
            "subjectOid": "OID-1",
            "subjectKey": "01-001",
            "subjectStatus": "Enrolled",
            "siteId": 128,
            "siteName": "Test Site",
            "enrollmentStartDate": "2024-11-04 16:03:19",
            "dateCreated": "2024-11-04 16:03:19",
            "dateModified": "2024-11-04 16:03:20",
        },
    }

    response = ApiResponse[SubjectModel].model_validate(response_data)
    assert isinstance(response.data, SubjectModel)
    assert response.data.subjectKey == "01-001"
