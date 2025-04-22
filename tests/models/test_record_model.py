from datetime import datetime

import pytest
from pydantic import ValidationError

from imednet_sdk.models.record import KeywordModel, RecordModel, RecordPostItem

VALID_KEYWORD_DATA = {
    "keywordName": "Data Entry Error",
    "keywordKey": "DEE",
    "keywordId": 15362,
    "dateAdded": "2024-11-04 16:03:19",
}

VALID_RECORD_DATA = {
    "studyKey": "PHARMADEMO",
    "intervalId": 99,
    "formId": 10202,
    "formKey": "AE",
    "siteId": 128,
    "recordId": 1,
    "recordOid": "REC-1",  # Now optional
    "recordType": "SUBJECT",
    "recordStatus": "Record Incomplete",
    "deleted": False,
    "dateCreated": "2024-11-04 16:03:19",
    "dateModified": "2024-11-04 16:03:20",
    "subjectId": 326,
    "subjectOid": "OID-1",  # Now optional
    "subjectKey": "123-456",
    "visitId": 1,  # Now required
    "parentRecordId": 34,
    "keywords": [VALID_KEYWORD_DATA],  # Now required
    "recordData": {  # Now required
        "dateCreated": "2018-10-18 06:21:46",
        "unvnum": "1",
        "dateModified": "2018-11-18 07:11:16",
        "aeser": "",
        "aeterm": "Bronchitis",
    },
    # Removed fields: siteName, dateUpdated, updatedByUserName, createdByUserName,
    # formInstance, intervalName, intervalInstance, recordIsLocked, recordIsArchived, data
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
    assert model.subjectKey == VALID_RECORD_DATA["subjectKey"]
    assert model.visitId == VALID_RECORD_DATA["visitId"]
    assert model.parentRecordId == VALID_RECORD_DATA["parentRecordId"]

    assert isinstance(model.keywords, list)
    assert len(model.keywords) == 1
    assert isinstance(model.keywords[0], KeywordModel)
    assert model.keywords[0].keywordId == VALID_KEYWORD_DATA["keywordId"]
    assert isinstance(model.keywords[0].dateAdded, datetime)

    assert isinstance(model.recordData, dict)
    assert model.recordData == VALID_RECORD_DATA["recordData"]


def test_record_model_optional_fields_none_or_missing():
    """Test validation when optional fields (recordOid, subjectOid, parentRecordId) are None or missing."""
    data_with_none = VALID_RECORD_DATA.copy()
    data_with_none["recordOid"] = None
    data_with_none["subjectOid"] = None
    data_with_none["parentRecordId"] = None

    model_none = RecordModel.model_validate(data_with_none)
    assert model_none.recordOid is None
    assert model_none.subjectOid is None
    assert model_none.parentRecordId is None
    # Check required fields are still valid
    assert model_none.visitId == VALID_RECORD_DATA["visitId"]
    # Validate keywords separately if direct comparison fails due to object identity
    assert len(model_none.keywords) == 1
    assert model_none.keywords[0].keywordId == VALID_KEYWORD_DATA["keywordId"]
    assert model_none.recordData == VALID_RECORD_DATA["recordData"]

    data_missing_optionals = VALID_RECORD_DATA.copy()
    del data_missing_optionals["recordOid"]
    del data_missing_optionals["subjectOid"]
    del data_missing_optionals["parentRecordId"]

    model_missing = RecordModel.model_validate(data_missing_optionals)
    assert model_missing.recordOid is None
    assert model_missing.subjectOid is None
    assert model_missing.parentRecordId is None
    # Check required fields are still valid
    assert model_missing.visitId == VALID_RECORD_DATA["visitId"]
    assert model_missing.keywords == [KeywordModel.model_validate(VALID_KEYWORD_DATA)]
    assert model_missing.recordData == VALID_RECORD_DATA["recordData"]


def test_record_model_empty_record_data_and_keywords():
    """Test validation with empty recordData and keywords list (now required)."""
    # Keywords and recordData are now required, so they cannot be empty lists/dicts
    # unless the schema allows empty lists/dicts for required fields.
    # Assuming empty list/dict is valid for required fields:
    data_empty = VALID_RECORD_DATA.copy()
    data_empty["keywords"] = []
    data_empty["recordData"] = {}

    model = RecordModel.model_validate(data_empty)
    assert model.keywords == []
    assert model.recordData == {}

    # Test if empty list/dict is NOT allowed for required fields (raises ValidationError)
    # This depends on Pydantic's behavior or specific validators
    # Example: Test missing keywords (should fail)
    data_missing_keywords = VALID_RECORD_DATA.copy()
    del data_missing_keywords["keywords"]
    with pytest.raises(ValidationError) as excinfo_keywords:
        RecordModel.model_validate(data_missing_keywords)
    assert "keywords" in str(excinfo_keywords.value)
    assert "Field required" in str(excinfo_keywords.value)

    # Example: Test missing recordData (should fail)
    data_missing_recordData = VALID_RECORD_DATA.copy()
    del data_missing_recordData["recordData"]
    with pytest.raises(ValidationError) as excinfo_recordData:
        RecordModel.model_validate(data_missing_recordData)
    assert "recordData" in str(excinfo_recordData.value)
    assert "Field required" in str(excinfo_recordData.value)


def test_record_model_missing_required_field():
    """Test ValidationError is raised when a required field is missing."""
    required_fields = [
        "studyKey",
        "intervalId",
        "formId",
        "formKey",
        "siteId",
        "recordId",
        "recordType",
        "recordStatus",
        "deleted",
        "dateCreated",
        "dateModified",
        "subjectId",
        "subjectKey",
        "visitId",
        "keywords",
        "recordData",
    ]
    for field in required_fields:
        invalid_data = VALID_RECORD_DATA.copy()
        if field in invalid_data:
            del invalid_data[field]
        else:
            pytest.fail(f"Required field '{field}' missing from VALID_RECORD_DATA for test setup.")

        with pytest.raises(ValidationError) as excinfo:
            RecordModel.model_validate(invalid_data)

        assert field in str(excinfo.value)
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
    assert "keywords" in str(excinfo_list.value).lower()

    invalid_data_list_item = VALID_RECORD_DATA.copy()
    invalid_data_list_item["keywords"] = [{"keywordId": "wrong_type"}]
    with pytest.raises(ValidationError) as excinfo_item:
        RecordModel.model_validate(invalid_data_list_item)
    assert "keywords.0.keywordId" in str(excinfo_item.value)


def test_record_model_serialization():
    """Test serialization of the RecordModel."""
    model = RecordModel.model_validate(VALID_RECORD_DATA)
    dump = model.model_dump(by_alias=True)

    expected_data = VALID_RECORD_DATA.copy()
    keyword_model = KeywordModel.model_validate(VALID_KEYWORD_DATA)
    expected_keyword_dump = keyword_model.model_dump(by_alias=True)

    # Check fields, excluding removed ones and handling optional/required changes
    for key, value in expected_data.items():
        # Skip removed fields
        if key in [
            "siteName",
            "dateUpdated",
            "updatedByUserName",
            "createdByUserName",
            "formInstance",
            "intervalName",
            "intervalInstance",
            "recordIsLocked",
            "recordIsArchived",
            "data",
        ]:
            continue

        if key not in ["dateCreated", "dateModified", "keywords", "recordData"]:
            # Handle optional fields that might be None in the dump
            if key in ["recordOid", "subjectOid", "parentRecordId"]:
                assert dump.get(key) == value
            else:
                assert dump[key] == value

    assert dump["dateCreated"] == datetime(2024, 11, 4, 16, 3, 19)
    assert dump["dateModified"] == datetime(2024, 11, 4, 16, 3, 20)

    assert isinstance(dump["keywords"], list)
    assert len(dump["keywords"]) == 1
    assert dump["keywords"][0] == expected_keyword_dump

    assert dump["recordData"] == expected_data["recordData"]

    # Test serialization with missing optional fields
    data_missing_optionals = VALID_RECORD_DATA.copy()
    del data_missing_optionals["recordOid"]
    del data_missing_optionals["subjectOid"]
    del data_missing_optionals["parentRecordId"]
    model_missing = RecordModel.model_validate(data_missing_optionals)
    dump_missing = model_missing.model_dump(
        by_alias=True, exclude_none=True
    )  # exclude_none is important here

    assert "recordOid" not in dump_missing
    assert "subjectOid" not in dump_missing
    assert "parentRecordId" not in dump_missing
    # Ensure required fields are still present
    assert "visitId" in dump_missing
    assert "keywords" in dump_missing
    assert "recordData" in dump_missing


VALID_POST_ITEM_REGISTER = {
    "formKey": "REG",
    "siteName": "Minneapolis",
    "data": {"textField": "Text value"},
}

VALID_POST_ITEM_UPDATE = {
    "formKey": "REG",
    "subjectKey": "651-042",
    "intervalName": "Registration",
    "data": {"textField": "Updated text"},
}

VALID_POST_ITEM_CREATE = {
    "formKey": "REG",
    "subjectKey": "123-876",
    "data": {"textField": "New record data"},
}

VALID_POST_ITEM_WITH_IDS = {
    "formId": 101,
    "siteId": 202,
    "subjectId": 303,
    "intervalId": 404,
    "recordId": 505,
    "formKey": "OTHER",
    "data": {"field": "value"},
}


def test_record_post_item_validation_required():
    """Test successful validation with only required fields."""
    data = {"formKey": "BASIC", "data": {"field1": "value1"}}
    model = RecordPostItem.model_validate(data)
    assert model.formKey == "BASIC"
    assert model.data == {"field1": "value1"}
    assert model.siteName is None
    assert model.subjectKey is None
    assert model.intervalName is None


def test_record_post_item_validation_scenarios():
    """Test successful validation for different scenarios from docs."""
    model_reg = RecordPostItem.model_validate(VALID_POST_ITEM_REGISTER)
    assert model_reg.formKey == "REG"
    assert model_reg.siteName == "Minneapolis"
    assert model_reg.subjectKey is None
    assert model_reg.data == {"textField": "Text value"}

    model_upd = RecordPostItem.model_validate(VALID_POST_ITEM_UPDATE)
    assert model_upd.formKey == "REG"
    assert model_upd.subjectKey == "651-042"
    assert model_upd.intervalName == "Registration"
    assert model_upd.siteName is None
    assert model_upd.data == {"textField": "Updated text"}

    model_cre = RecordPostItem.model_validate(VALID_POST_ITEM_CREATE)
    assert model_cre.formKey == "REG"
    assert model_cre.subjectKey == "123-876"
    assert model_cre.intervalName is None
    assert model_cre.siteName is None
    assert model_cre.data == {"textField": "New record data"}


def test_record_post_item_validation_with_ids():
    """Test successful validation when using optional ID fields."""
    model = RecordPostItem.model_validate(VALID_POST_ITEM_WITH_IDS)
    assert model.formId == 101
    assert model.siteId == 202
    assert model.subjectId == 303
    assert model.intervalId == 404
    assert model.recordId == 505
    assert model.formKey == "OTHER"
    assert model.data == {"field": "value"}


def test_record_post_item_missing_required():
    """Test ValidationError when required fields (formKey, data) are missing."""
    with pytest.raises(ValidationError) as excinfo_form:
        RecordPostItem.model_validate({"data": {"f": 1}})
    assert "formKey" in str(excinfo_form.value)

    with pytest.raises(ValidationError) as excinfo_data:
        RecordPostItem.model_validate({"formKey": "FK"})
    assert "data" in str(excinfo_data.value)


def test_record_post_item_invalid_type():
    """Test ValidationError for incorrect data types."""
    invalid_data = VALID_POST_ITEM_REGISTER.copy()
    invalid_data["data"] = "not-a-dict"
    with pytest.raises(ValidationError) as excinfo:
        RecordPostItem.model_validate(invalid_data)
    assert "data" in str(excinfo.value)
    assert "Input should be a valid dictionary" in str(excinfo.value)

    invalid_data_id = VALID_POST_ITEM_WITH_IDS.copy()
    invalid_data_id["formId"] = "not-an-int"
    with pytest.raises(ValidationError) as excinfo_id:
        RecordPostItem.model_validate(invalid_data_id)
    assert "formId" in str(excinfo_id.value)
    assert "Input should be a valid integer" in str(excinfo_id.value)


def test_record_post_item_serialization():
    """Test serialization of RecordPostItem."""
    model = RecordPostItem.model_validate(VALID_POST_ITEM_UPDATE)
    dump = model.model_dump(by_alias=True, exclude_none=True)

    expected_dump = {
        "formKey": "REG",
        "subjectKey": "651-042",
        "intervalName": "Registration",
        "data": {"textField": "Updated text"},
    }
    assert dump == expected_dump

    model_ids = RecordPostItem.model_validate(VALID_POST_ITEM_WITH_IDS)
    dump_ids = model_ids.model_dump(by_alias=True, exclude_none=True)
    expected_dump_ids = {
        "formId": 101,
        "siteId": 202,
        "subjectId": 303,
        "intervalId": 404,
        "recordId": 505,
        "formKey": "OTHER",
        "data": {"field": "value"},
    }
    assert dump_ids == expected_dump_ids
