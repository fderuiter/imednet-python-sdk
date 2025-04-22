# filepath: /Users/fred/Documents/GitHub/imednet-python-sdk/tests/models/test_query_model.py
from datetime import datetime

import pytest
from pydantic import ValidationError

from imednet_sdk.api.queries import QueryCommentModel, QueryModel

# Sample valid data based on docs/reference/queries.md
VALID_QUERY_COMMENT_DATA = {
    "sequence": 1,
    "annotationStatus": "Monitor Query Open",
    "user": "john",
    "comment": "Added comment to study",
    "closed": False,
    "date": "2024-11-04 16:03:19",
}

VALID_QUERY_DATA = {
    "studyKey": "PHARMADEMO",
    "subjectId": 1,
    "subjectOid": "OID-1",
    "annotationType": "subject",
    "annotationId": 1,
    "type": None,  # Optional field
    "description": "Monitor Query",
    "recordId": 123,  # Optional field
    "variable": "aeterm",  # Optional field
    "subjectKey": "123-005",
    "dateCreated": "2024-11-04 16:03:19",
    "dateModified": "2024-11-04 16:03:20",
    "queryComments": [VALID_QUERY_COMMENT_DATA],
}

# --- QueryCommentModel Tests ---


def test_query_comment_model_validation():
    """Test successful validation of QueryCommentModel."""
    model = QueryCommentModel.model_validate(VALID_QUERY_COMMENT_DATA)
    assert model.sequence == VALID_QUERY_COMMENT_DATA["sequence"]
    assert model.annotationStatus == VALID_QUERY_COMMENT_DATA["annotationStatus"]
    assert model.user == VALID_QUERY_COMMENT_DATA["user"]
    assert model.comment == VALID_QUERY_COMMENT_DATA["comment"]
    assert model.closed == VALID_QUERY_COMMENT_DATA["closed"]
    assert isinstance(model.date, datetime)
    assert model.date == datetime(2024, 11, 4, 16, 3, 19)


def test_query_comment_model_missing_required():
    """Test ValidationError for missing required field in QueryCommentModel."""
    invalid_data = VALID_QUERY_COMMENT_DATA.copy()
    del invalid_data["user"]
    with pytest.raises(ValidationError):
        QueryCommentModel.model_validate(invalid_data)


def test_query_comment_model_invalid_type():
    """Test ValidationError for invalid type in QueryCommentModel."""
    invalid_data = VALID_QUERY_COMMENT_DATA.copy()
    invalid_data["sequence"] = "not-an-int"
    with pytest.raises(ValidationError):
        QueryCommentModel.model_validate(invalid_data)


# --- QueryModel Tests ---


def test_query_model_validation():
    """Test successful validation of QueryModel with valid data."""
    model = QueryModel.model_validate(VALID_QUERY_DATA)

    assert model.studyKey == VALID_QUERY_DATA["studyKey"]
    assert model.subjectId == VALID_QUERY_DATA["subjectId"]
    assert model.subjectOid == VALID_QUERY_DATA["subjectOid"]
    assert model.annotationType == VALID_QUERY_DATA["annotationType"]
    assert model.annotationId == VALID_QUERY_DATA["annotationId"]
    assert model.type == VALID_QUERY_DATA["type"]
    assert model.description == VALID_QUERY_DATA["description"]
    assert model.recordId == VALID_QUERY_DATA["recordId"]
    assert model.variable == VALID_QUERY_DATA["variable"]
    assert model.subjectKey == VALID_QUERY_DATA["subjectKey"]
    assert isinstance(model.dateCreated, datetime)
    assert model.dateCreated == datetime(2024, 11, 4, 16, 3, 19)
    assert isinstance(model.dateModified, datetime)
    assert model.dateModified == datetime(2024, 11, 4, 16, 3, 20)

    assert isinstance(model.queryComments, list)
    assert len(model.queryComments) == 1
    assert isinstance(model.queryComments[0], QueryCommentModel)
    assert model.queryComments[0].sequence == VALID_QUERY_COMMENT_DATA["sequence"]


def test_query_model_optional_fields_missing():
    """Test validation when optional fields are missing."""
    data_missing_optionals = VALID_QUERY_DATA.copy()
    del data_missing_optionals["type"]
    del data_missing_optionals["recordId"]
    del data_missing_optionals["variable"]

    model = QueryModel.model_validate(data_missing_optionals)
    assert model.type is None
    assert model.recordId is None
    assert model.variable is None


def test_query_model_missing_required_field():
    """Test ValidationError is raised when a required field is missing."""
    invalid_data = VALID_QUERY_DATA.copy()
    del invalid_data["description"]  # Remove a required field

    with pytest.raises(ValidationError) as excinfo:
        QueryModel.model_validate(invalid_data)

    assert "description" in str(excinfo.value)
    assert "Field required" in str(excinfo.value)


def test_query_model_invalid_data_type():
    """Test ValidationError is raised for incorrect data types."""
    invalid_data = VALID_QUERY_DATA.copy()
    invalid_data["subjectId"] = "not-an-integer"

    with pytest.raises(ValidationError) as excinfo:
        QueryModel.model_validate(invalid_data)

    assert "subjectId" in str(excinfo.value)
    assert "Input should be a valid integer" in str(excinfo.value)

    invalid_data_list = VALID_QUERY_DATA.copy()
    invalid_data_list["queryComments"] = "not-a-list"
    with pytest.raises(ValidationError) as excinfo_list:
        QueryModel.model_validate(invalid_data_list)
    assert "queryComments" in str(excinfo_list.value)
    assert "Input should be a valid list" in str(excinfo_list.value)

    invalid_data_list_item = VALID_QUERY_DATA.copy()
    invalid_data_list_item["queryComments"] = [{"sequence": "wrong_type"}]  # Invalid item
    with pytest.raises(ValidationError) as excinfo_item:
        QueryModel.model_validate(invalid_data_list_item)
    assert "queryComments.0.sequence" in str(excinfo_item.value)


def test_query_model_serialization():
    """Test serialization of the QueryModel."""
    model = QueryModel.model_validate(VALID_QUERY_DATA)
    dump = model.model_dump(by_alias=True)

    expected_data = VALID_QUERY_DATA.copy()
    # Adjust datetime serialization if needed

    # Check basic fields match
    for key, value in expected_data.items():
        if key not in ["dateCreated", "dateModified", "queryComments"]:
            assert dump[key] == value

    # Check datetime serialization
    assert dump["dateCreated"] == datetime(2024, 11, 4, 16, 3, 19)
    assert dump["dateModified"] == datetime(2024, 11, 4, 16, 3, 20)

    # Check nested model serialization
    assert isinstance(dump["queryComments"], list)
    assert len(dump["queryComments"]) == 1
    # Need to dump the nested model for comparison if it contains datetimes
    nested_model = QueryCommentModel.model_validate(VALID_QUERY_COMMENT_DATA)
    expected_nested_dump = nested_model.model_dump(by_alias=True)
    assert dump["queryComments"][0] == expected_nested_dump


# Add more tests for edge cases, different annotation types, etc.
