# filepath: /Users/fred/Documents/GitHub/imednet-python-sdk/tests/models/test_coding_model.py
from datetime import datetime

import pytest
from pydantic import ValidationError

from imednet_sdk.models.coding import CodingModel

# Sample valid data based on docs/reference/codings.md
VALID_CODING_DATA = {
    "studyKey": "PHARMADEMO",
    "siteName": "Chicago Hope Hospital",
    "siteId": 128,
    "subjectId": 247,
    "subjectKey": "111-005",
    "formId": 1,
    "formName": "Adverse Event",
    "formKey": "AE",
    "revision": 2,
    "recordId": 1,
    "variable": "AETERM",
    "value": "Angina",
    "codingId": 1,
    "code": "Angina agranulocytic",
    "codedBy": "John Smith",
    "reason": "Typo fix",
    "dictionaryName": "MedDRA",
    "dictionaryVersion": "24.0",
    "dateCoded": "2024-11-04 16:03:19",  # Example format
}


def test_coding_model_validation():
    """Test successful validation of CodingModel with valid data."""
    model = CodingModel.model_validate(VALID_CODING_DATA)

    assert model.studyKey == VALID_CODING_DATA["studyKey"]
    assert model.siteName == VALID_CODING_DATA["siteName"]
    assert model.siteId == VALID_CODING_DATA["siteId"]
    assert model.subjectId == VALID_CODING_DATA["subjectId"]
    assert model.subjectKey == VALID_CODING_DATA["subjectKey"]
    assert model.formId == VALID_CODING_DATA["formId"]
    assert model.formName == VALID_CODING_DATA["formName"]
    assert model.formKey == VALID_CODING_DATA["formKey"]
    assert model.revision == VALID_CODING_DATA["revision"]
    assert model.recordId == VALID_CODING_DATA["recordId"]
    assert model.variable == VALID_CODING_DATA["variable"]
    assert model.value == VALID_CODING_DATA["value"]
    assert model.codingId == VALID_CODING_DATA["codingId"]
    assert model.code == VALID_CODING_DATA["code"]
    assert model.codedBy == VALID_CODING_DATA["codedBy"]
    assert model.reason == VALID_CODING_DATA["reason"]
    assert model.dictionaryName == VALID_CODING_DATA["dictionaryName"]
    assert model.dictionaryVersion == VALID_CODING_DATA["dictionaryVersion"]
    # Pydantic v2 automatically parses common datetime formats
    assert isinstance(model.dateCoded, datetime)
    assert model.dateCoded == datetime(2024, 11, 4, 16, 3, 19)


def test_coding_model_missing_required_field():
    """Test ValidationError is raised when a required field is missing."""
    invalid_data = VALID_CODING_DATA.copy()
    del invalid_data["studyKey"]  # Remove a required field

    with pytest.raises(ValidationError) as excinfo:
        CodingModel.model_validate(invalid_data)

    # Check that the error message mentions the missing field
    assert "studyKey" in str(excinfo.value)
    assert "Field required" in str(excinfo.value)


def test_coding_model_invalid_data_type():
    """Test ValidationError is raised for incorrect data types."""
    invalid_data = VALID_CODING_DATA.copy()
    invalid_data["siteId"] = "not-an-integer"  # Incorrect type

    with pytest.raises(ValidationError) as excinfo:
        CodingModel.model_validate(invalid_data)

    assert "siteId" in str(excinfo.value)
    assert "Input should be a valid integer" in str(excinfo.value)


def test_coding_model_serialization():
    """Test serialization of the CodingModel."""
    model = CodingModel.model_validate(VALID_CODING_DATA)
    # Use by_alias=True if field names differ from API keys
    # (which they do, camelCase vs snake_case if we used aliases)
    # However, since we are using camelCase directly in the model,
    # by_alias=True is not strictly needed
    # unless we explicitly defined aliases. Let's keep it for consistency if needed later.
    dump = model.model_dump(by_alias=True)  # Pydantic v2 uses model_dump

    # Convert datetime back to string format expected in the original data for comparison
    expected_data = VALID_CODING_DATA.copy()
    # Pydantic v2 might serialize datetime differently, adjust if needed
    # expected_data["dateCoded"] = model.dateCoded.isoformat() # Example if isoformat is used

    # Check basic fields match
    for key, value in expected_data.items():
        if key != "dateCoded":  # Handle datetime separately if format differs
            assert dump[key] == value

    # Check datetime serialization (adjust format as needed based on actual output)
    # This assumes default Pydantic v2 serialization for datetime
    assert dump["dateCoded"] == datetime(2024, 11, 4, 16, 3, 19)


# Add more tests for edge cases, optional fields (if any), specific validations etc.
