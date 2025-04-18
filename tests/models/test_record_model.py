import pytest
from pydantic import ValidationError
from datetime import datetime
from typing import List, Optional, Dict, Any

from imednet_sdk.models.record import RecordModel
from imednet_sdk.models.subject import KeywordModel # Import KeywordModel

# Sample valid data based on docs/reference/records.md and subject.py (for KeywordModel)
VALID_KEYWORD_DATA = {
    "keywordName": "Data Entry Error",
    "keywordKey": "DEE",
    "keywordId": 15362,
    "dateAdded": "2024-11-04 16:03:19"
}

VALID_RECORD_DATA = {
    "studyKey": "PHARMADEMO",
    "intervalId": 99,
    "formId": 10202,
    "formKey": "AE",
    "siteId": 128,
    "recordId": 1,
    "recordOid": "REC-1",
    "recordType": "SUBJECT",
    "recordStatus": "Record Incomplete",
    "deleted": False,
    "dateCreated": "2024-11-04 16:03:19",
    "dateModified": "2024-11-04 16:03:20",
    "subjectId": 326,
    "subjectOid": "OID-1",
    "subjectKey": "123-456",
    "visitId": 1, # Optional
    "parentRecordId": 34, # Optional
    "keywords": [VALID_KEYWORD_DATA], # Optional list of KeywordModel
    "recordData": { # Dynamic data
        "dateCreated": "2018-10-18 06:21:46",
        "unvnum": "1",
        "dateModified": "2018-11-18 07:11:16",
        "aeser": "",
        "aeterm": "Bronchitis"
    }
}

def test_record_model_validation():
    """Test successful validation of RecordModel with valid data."""
    model = RecordModel.model_validate(VALID_RECORD_DATA)

    assert model.studyKey == VALID_RECORD_DATA["studyKey"]
    assert model.intervalId == VALID_RECORD_DATA["intervalId"]
    assert model.formId == VALID_RECORD_DATA["formId"]
    assert model.formKey == VALID_RECORD_DATA["formKey"]
    assert model.siteId == VALID_RECORD_DATA["siteId"]
    assert model.recordId == VALID_RECORD_DATA["recordId"]
    assert model.recordOid == VALID_RECORD_DATA["recordOid"]
    assert model.recordType == VALID_RECORD_DATA["recordType"]
    assert model.recordStatus == VALID_RECORD_DATA["recordStatus"]
    assert model.deleted == VALID_RECORD_DATA["deleted"]
    assert isinstance(model.dateCreated, datetime)
    assert model.dateCreated == datetime(2024, 11, 4, 16, 3, 19)
    assert isinstance(model.dateModified, datetime)
    assert model.dateModified == datetime(2024, 11, 4, 16, 3, 20)
    assert model.subjectId == VALID_RECORD_DATA["subjectId"]
    assert model.subjectOid == VALID_RECORD_DATA["subjectOid"]
    assert model.subjectKey == VALID_RECORD_DATA["subjectKey"]
    assert model.visitId == VALID_RECORD_DATA["visitId"]
    assert model.parentRecordId == VALID_RECORD_DATA["parentRecordId"]

    assert isinstance(model.keywords, list)
    assert len(model.keywords) == 1
    assert isinstance(model.keywords[0], KeywordModel)
    assert model.keywords[0].keywordId == VALID_KEYWORD_DATA["keywordId"] # Use camelCase for nested model attribute
    assert isinstance(model.keywords[0].dateAdded, datetime) # Use camelCase for nested model attribute

    assert isinstance(model.recordData, dict)
    assert model.recordData == VALID_RECORD_DATA["recordData"]

def test_record_model_optional_fields_none_or_missing():
    """Test validation when optional fields are None or missing."""
    data_with_none = VALID_RECORD_DATA.copy()
    data_with_none["visitId"] = None
    data_with_none["parentRecordId"] = None
    data_with_none["keywords"] = None

    model_none = RecordModel.model_validate(data_with_none)
    assert model_none.visitId is None
    assert model_none.parentRecordId is None
    assert model_none.keywords is None

    data_missing_optionals = VALID_RECORD_DATA.copy()
    del data_missing_optionals["visitId"]
    del data_missing_optionals["parentRecordId"]
    del data_missing_optionals["keywords"]

    model_missing = RecordModel.model_validate(data_missing_optionals)
    assert model_missing.visitId is None
    assert model_missing.parentRecordId is None
    assert model_missing.keywords is None

def test_record_model_empty_record_data_and_keywords():
    """Test validation with empty recordData and keywords list."""
    data_empty = VALID_RECORD_DATA.copy()
    data_empty["keywords"] = []
    data_empty["recordData"] = {}

    model = RecordModel.model_validate(data_empty)
    assert model.keywords == []
    assert model.recordData == {}

def test_record_model_missing_required_field():
    """Test ValidationError is raised when a required field is missing."""
    invalid_data = VALID_RECORD_DATA.copy()
    del invalid_data["formKey"] # Remove a required field

    with pytest.raises(ValidationError) as excinfo:
        RecordModel.model_validate(invalid_data)

    assert "formKey" in str(excinfo.value)
    assert "Field required" in str(excinfo.value)

def test_record_model_invalid_data_type():
    """Test ValidationError is raised for incorrect data types."""
    invalid_data = VALID_RECORD_DATA.copy()
    invalid_data["recordId"] = "not-an-integer"

    with pytest.raises(ValidationError) as excinfo:
        RecordModel.model_validate(invalid_data)

    assert "recordId" in str(excinfo.value)
    assert "Input should be a valid integer" in str(excinfo.value)

    invalid_data_dict = VALID_RECORD_DATA.copy()
    invalid_data_dict["recordData"] = "not-a-dict"
    with pytest.raises(ValidationError) as excinfo_dict:
        RecordModel.model_validate(invalid_data_dict)
    assert "recordData" in str(excinfo_dict.value)
    assert "Input should be a valid dictionary" in str(excinfo_dict.value)

    invalid_data_list = VALID_RECORD_DATA.copy()
    invalid_data_list["keywords"] = "not-a-list"
    with pytest.raises(ValidationError) as excinfo_list:
        RecordModel.model_validate(invalid_data_list)
    assert "keywords" in str(excinfo_list.value)
    # Error message might differ slightly
    assert "list" in str(excinfo_list.value).lower()

    invalid_data_list_item = VALID_RECORD_DATA.copy()
    invalid_data_list_item["keywords"] = [{"keywordId": "wrong_type"}] # Invalid item
    with pytest.raises(ValidationError) as excinfo_item:
        RecordModel.model_validate(invalid_data_list_item)
    assert "keywords.0.keywordId" in str(excinfo_item.value)

def test_record_model_serialization():
    """Test serialization of the RecordModel."""
    model = RecordModel.model_validate(VALID_RECORD_DATA)
    dump = model.model_dump(by_alias=True)

    expected_data = VALID_RECORD_DATA.copy()
    # Adjust datetime and nested model serialization if needed
    keyword_model = KeywordModel.model_validate(VALID_KEYWORD_DATA)
    expected_keyword_dump = keyword_model.model_dump(by_alias=True)

    # Check basic fields match
    for key, value in expected_data.items():
        if key not in ["dateCreated", "dateModified", "keywords", "recordData"]:
            assert dump[key] == value

    # Check datetime serialization
    assert dump["dateCreated"] == datetime(2024, 11, 4, 16, 3, 19)
    assert dump["dateModified"] == datetime(2024, 11, 4, 16, 3, 20)

    # Check nested KeywordModel serialization
    assert isinstance(dump["keywords"], list)
    assert len(dump["keywords"]) == 1
    assert dump["keywords"][0] == expected_keyword_dump

    # Check recordData serialization (should be the same dict)
    assert dump["recordData"] == expected_data["recordData"]

# Add more tests for edge cases, different recordData structures, etc.
