"""Tests for subject-related models."""

from datetime import datetime
from typing import List

import pytest
from pydantic import TypeAdapter, ValidationError

from imednet_sdk.api._base import ApiResponse
from imednet_sdk.api.subjects import KeywordModel, SubjectModel

# Sample valid data based on docs/reference/subjects.md
VALID_KEYWORD_DATA = {
    "keywordName": "Data Entry Error",
    "keywordKey": "DEE",
    "keywordId": 15362,
    "dateAdded": "2024-11-04 16:03:19",
}

VALID_SUBJECT_DATA = {
    "studyKey": "PHARMADEMO",
    "subjectId": 1,
    "subjectOid": "OID-1",  # Still provide in base valid data
    "subjectKey": "01-001",
    "subjectStatus": "Enrolled",
    "siteId": 128,
    "siteName": "Chicago Hope Hospital",
    "deleted": False,  # Explicitly setting default
    "enrollmentStartDate": "2024-11-04 16:03:19",  # Still provide in base valid data
    "dateCreated": "2024-11-04 16:03:19",
    "dateModified": "2024-11-04 16:03:20",
    "keywords": [VALID_KEYWORD_DATA],  # Optional list of KeywordModel
}

# --- KeywordModel Tests ---


def test_keyword_model_validation():
    """Test successful validation of KeywordModel."""
    model = KeywordModel.model_validate(VALID_KEYWORD_DATA)
    assert model.keywordName == VALID_KEYWORD_DATA["keywordName"]
    assert model.keywordKey == VALID_KEYWORD_DATA["keywordKey"]
    assert model.keywordId == VALID_KEYWORD_DATA["keywordId"]
    assert isinstance(model.dateAdded, datetime)
    assert model.dateAdded == datetime(2024, 11, 4, 16, 3, 19)


def test_keyword_model_missing_required_field():
    """Test ValidationError is raised when a required field is missing."""
    invalid_data = VALID_KEYWORD_DATA.copy()
    del invalid_data["keywordKey"]
    with pytest.raises(ValidationError) as excinfo:
        KeywordModel.model_validate(invalid_data)
    assert "keywordKey" in str(excinfo.value)


def test_keyword_model_invalid_data_type():
    """Test ValidationError is raised for incorrect data types."""
    invalid_data = VALID_KEYWORD_DATA.copy()
    invalid_data["keywordId"] = "not-an-int"
    with pytest.raises(ValidationError) as excinfo:
        KeywordModel.model_validate(invalid_data)
    assert "keywordId" in str(excinfo.value)


# --- SubjectModel Tests ---


def test_subject_model_validation():
    """Test successful validation of SubjectModel with valid data."""
    model = SubjectModel.model_validate(VALID_SUBJECT_DATA)

    assert model.studyKey == VALID_SUBJECT_DATA["studyKey"]
    assert model.subjectId == VALID_SUBJECT_DATA["subjectId"]
    assert model.subjectOid == VALID_SUBJECT_DATA["subjectOid"]
    assert model.subjectKey == VALID_SUBJECT_DATA["subjectKey"]
    assert model.subjectStatus == VALID_SUBJECT_DATA["subjectStatus"]
    assert model.siteId == VALID_SUBJECT_DATA["siteId"]
    assert model.siteName == VALID_SUBJECT_DATA["siteName"]
    assert model.deleted == VALID_SUBJECT_DATA["deleted"]
    assert isinstance(model.enrollmentStartDate, datetime)
    assert model.enrollmentStartDate == datetime(2024, 11, 4, 16, 3, 19)
    assert isinstance(model.dateCreated, datetime)
    assert model.dateCreated == datetime(2024, 11, 4, 16, 3, 19)
    assert isinstance(model.dateModified, datetime)
    assert model.dateModified == datetime(2024, 11, 4, 16, 3, 20)

    assert isinstance(model.keywords, list)
    assert len(model.keywords) == 1
    assert isinstance(model.keywords[0], KeywordModel)
    assert model.keywords[0].keywordId == VALID_KEYWORD_DATA["keywordId"]


def test_subject_model_optional_fields_none_or_missing():
    """Test validation when optional fields are None or missing."""
    # Test with keywords=None
    data_with_none_keywords = VALID_SUBJECT_DATA.copy()
    data_with_none_keywords["keywords"] = None
    model_none_keywords = SubjectModel.model_validate(data_with_none_keywords)
    assert model_none_keywords.keywords is None

    # Test with subjectOid=None
    data_with_none_oid = VALID_SUBJECT_DATA.copy()
    data_with_none_oid["subjectOid"] = None
    model_none_oid = SubjectModel.model_validate(data_with_none_oid)
    assert model_none_oid.subjectOid is None

    # Test with enrollmentStartDate=None
    data_with_none_enroll = VALID_SUBJECT_DATA.copy()
    data_with_none_enroll["enrollmentStartDate"] = None
    model_none_enroll = SubjectModel.model_validate(data_with_none_enroll)
    assert model_none_enroll.enrollmentStartDate is None

    # Test with missing optional fields
    data_missing_optionals = VALID_SUBJECT_DATA.copy()
    del data_missing_optionals["keywords"]
    del data_missing_optionals["subjectOid"]
    del data_missing_optionals["enrollmentStartDate"]

    model_missing = SubjectModel.model_validate(data_missing_optionals)
    assert model_missing.keywords is None
    assert model_missing.subjectOid is None
    assert model_missing.enrollmentStartDate is None


def test_subject_model_defaults():
    """Test default values for boolean fields when not provided."""
    minimal_data = VALID_SUBJECT_DATA.copy()
    del minimal_data["deleted"]
    del minimal_data["keywords"]  # Remove optional field for minimal test

    model = SubjectModel.model_validate(minimal_data)
    assert model.deleted is False
    assert model.keywords is None


def test_subject_model_missing_required_field():
    """Test ValidationError is raised when a required field is missing."""
    invalid_data = VALID_SUBJECT_DATA.copy()
    del invalid_data["subjectKey"]  # Remove a required field

    with pytest.raises(ValidationError) as excinfo:
        SubjectModel.model_validate(invalid_data)

    assert "subjectKey" in str(excinfo.value)
    assert "Field required" in str(excinfo.value)


def test_subject_model_invalid_data_type():
    """Test ValidationError is raised for incorrect data types."""
    invalid_data = VALID_SUBJECT_DATA.copy()
    invalid_data["subjectId"] = "not-an-integer"

    with pytest.raises(ValidationError) as excinfo:
        SubjectModel.model_validate(invalid_data)

    assert "subjectId" in str(excinfo.value)
    assert "Input should be a valid integer" in str(excinfo.value)

    invalid_data_list = VALID_SUBJECT_DATA.copy()
    invalid_data_list["keywords"] = "not-a-list"
    with pytest.raises(ValidationError) as excinfo_list:
        SubjectModel.model_validate(invalid_data_list)
    assert "keywords" in str(excinfo_list.value)
    assert "list" in str(excinfo_list.value).lower()

    invalid_data_list_item = VALID_SUBJECT_DATA.copy()
    invalid_data_list_item["keywords"] = [{"keywordId": "wrong_type"}]  # Invalid item
    with pytest.raises(ValidationError) as excinfo_item:
        SubjectModel.model_validate(invalid_data_list_item)
    assert "keywords.0.keywordId" in str(excinfo_item.value)


def test_subject_model_serialization():
    """Test serialization of the SubjectModel."""
    model = SubjectModel.model_validate(VALID_SUBJECT_DATA)
    dump = model.model_dump(by_alias=True)

    expected_data = VALID_SUBJECT_DATA.copy()
    # Adjust datetime and nested model serialization if needed
    keyword_model = KeywordModel.model_validate(VALID_KEYWORD_DATA)
    expected_keyword_dump = keyword_model.model_dump(by_alias=True)

    # Check basic fields match
    for key, value in expected_data.items():
        if key not in ["enrollmentStartDate", "dateCreated", "dateModified", "keywords"]:
            assert dump[key] == value

    # Check datetime serialization (if present)
    if model.enrollmentStartDate:
        assert dump["enrollmentStartDate"] == datetime(2024, 11, 4, 16, 3, 19)
    else:
        assert dump["enrollmentStartDate"] is None
    assert dump["dateCreated"] == datetime(2024, 11, 4, 16, 3, 19)
    assert dump["dateModified"] == datetime(2024, 11, 4, 16, 3, 20)

    # Check nested KeywordModel serialization
    assert isinstance(dump["keywords"], list)
    assert len(dump["keywords"]) == 1
    assert dump["keywords"][0] == expected_keyword_dump

    # Test serialization with missing optional fields
    data_missing_optionals = VALID_SUBJECT_DATA.copy()
    del data_missing_optionals["keywords"]
    del data_missing_optionals["subjectOid"]
    del data_missing_optionals["enrollmentStartDate"]
    model_missing = SubjectModel.model_validate(data_missing_optionals)
    dump_missing = model_missing.model_dump(by_alias=True)

    assert "keywords" not in dump_missing or dump_missing["keywords"] is None
    assert "subjectOid" not in dump_missing or dump_missing["subjectOid"] is None
    assert "enrollmentStartDate" not in dump_missing or dump_missing["enrollmentStartDate"] is None


# Add more tests for edge cases, different subject statuses, etc.


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
            # "subjectOid": "OID-1", # Test missing optional
            "subjectKey": "01-001",
            "subjectStatus": "Enrolled",
            "siteId": 128,
            "siteName": "Test Site",
            # "enrollmentStartDate": "2024-11-04 16:03:19", # Test missing optional
            "dateCreated": "2024-11-04 16:03:19",
            "dateModified": "2024-11-04 16:03:20",
        },
    }

    response = ApiResponse[SubjectModel].model_validate(response_data)
    assert isinstance(response.data, SubjectModel)
    assert response.data.subjectKey == "01-001"
    assert response.data.subjectOid is None
    assert response.data.enrollmentStartDate is None
