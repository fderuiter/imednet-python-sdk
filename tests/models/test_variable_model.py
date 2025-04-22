from datetime import datetime

import pytest
from pydantic import ValidationError

from imednet_sdk.models.variable import VariableModel

# Sample valid data based on docs/reference/variables.md
VALID_VARIABLE_DATA = {
    "studyKey": "PHARMADEMO",
    "variableId": 1,
    "variableType": "RADIO",
    "variableName": "Pain Level",
    "sequence": 1,
    "revision": 1,
    "disabled": False,  # Explicitly setting default
    "dateCreated": "2024-11-04 16:03:19",
    "dateModified": "2024-11-04 16:03:20",
    "formId": 108727,
    "variableOid": "OID-1", # Now optional
    "deleted": False,  # Explicitly setting default
    "formKey": "FORM_1",
    "formName": "Pre-procedure screening",
    "label": "Select patient pain level between 1 and 10",
    "blinded": False,  # Explicitly setting default
}


def test_variable_model_validation():
    """Test successful validation of VariableModel with valid data."""
    model = VariableModel.model_validate(VALID_VARIABLE_DATA)

    assert model.studyKey == VALID_VARIABLE_DATA["studyKey"]
    assert model.variableId == VALID_VARIABLE_DATA["variableId"]
    assert model.variableType == VALID_VARIABLE_DATA["variableType"]
    assert model.variableName == VALID_VARIABLE_DATA["variableName"]
    assert model.sequence == VALID_VARIABLE_DATA["sequence"]
    assert model.revision == VALID_VARIABLE_DATA["revision"]
    assert model.disabled == VALID_VARIABLE_DATA["disabled"]
    assert isinstance(model.dateCreated, datetime)
    assert model.dateCreated == datetime(2024, 11, 4, 16, 3, 19)
    assert isinstance(model.dateModified, datetime)
    assert model.dateModified == datetime(2024, 11, 4, 16, 3, 20)
    assert model.formId == VALID_VARIABLE_DATA["formId"]
    assert model.variableOid == VALID_VARIABLE_DATA["variableOid"]
    assert model.deleted == VALID_VARIABLE_DATA["deleted"]
    assert model.formKey == VALID_VARIABLE_DATA["formKey"]
    assert model.formName == VALID_VARIABLE_DATA["formName"]
    assert model.label == VALID_VARIABLE_DATA["label"]
    assert model.blinded == VALID_VARIABLE_DATA["blinded"]


def test_variable_model_optional_oid():
    """Test validation when optional variableOid is None or missing."""
    # Test with variableOid=None
    data_with_none_oid = VALID_VARIABLE_DATA.copy()
    data_with_none_oid["variableOid"] = None
    model_none_oid = VariableModel.model_validate(data_with_none_oid)
    assert model_none_oid.variableOid is None

    # Test with missing variableOid
    data_missing_oid = VALID_VARIABLE_DATA.copy()
    del data_missing_oid["variableOid"]
    model_missing_oid = VariableModel.model_validate(data_missing_oid)
    assert model_missing_oid.variableOid is None


def test_variable_model_defaults():
    """Test default values for boolean fields when not provided."""
    minimal_data = VALID_VARIABLE_DATA.copy()
    del minimal_data["disabled"]
    del minimal_data["deleted"]
    del minimal_data["blinded"]
    del minimal_data["variableOid"] # Also remove optional oid

    model = VariableModel.model_validate(minimal_data)
    assert model.disabled is False
    assert model.deleted is False
    assert model.blinded is False


def test_variable_model_missing_required_field():
    """Test ValidationError is raised when a required field is missing."""
    invalid_data = VALID_VARIABLE_DATA.copy()
    del invalid_data["variableName"]  # Remove a required field

    with pytest.raises(ValidationError) as excinfo:
        VariableModel.model_validate(invalid_data)

    assert "variableName" in str(excinfo.value)
    assert "Field required" in str(excinfo.value)


def test_variable_model_invalid_data_type():
    """Test ValidationError is raised for incorrect data types."""
    invalid_data = VALID_VARIABLE_DATA.copy()
    invalid_data["variableId"] = "not-an-integer"

    with pytest.raises(ValidationError) as excinfo:
        VariableModel.model_validate(invalid_data)

    assert "variableId" in str(excinfo.value)
    assert "Input should be a valid integer" in str(excinfo.value)

    invalid_data_bool = VALID_VARIABLE_DATA.copy()
    invalid_data_bool["disabled"] = "maybe"
    with pytest.raises(ValidationError) as excinfo_bool:
        VariableModel.model_validate(invalid_data_bool)

    assert "disabled" in str(excinfo_bool.value)
    assert "Input should be a valid boolean" in str(excinfo_bool.value)


def test_variable_model_serialization():
    """Test serialization of the VariableModel."""
    model = VariableModel.model_validate(VALID_VARIABLE_DATA)
    dump = model.model_dump(by_alias=True)

    expected_data = VALID_VARIABLE_DATA.copy()
    # Adjust datetime serialization if needed

    # Check basic fields match
    for key, value in expected_data.items():
        if key not in ["dateCreated", "dateModified"]:
            # Handle optional variableOid
            if key == "variableOid":
                assert dump.get(key) == value
            else:
                assert dump[key] == value

    # Check datetime serialization
    assert dump["dateCreated"] == datetime(2024, 11, 4, 16, 3, 19)
    assert dump["dateModified"] == datetime(2024, 11, 4, 16, 3, 20)

    # Test serialization with missing optional oid
    data_missing_oid = VALID_VARIABLE_DATA.copy()
    del data_missing_oid["variableOid"]
    model_missing = VariableModel.model_validate(data_missing_oid)
    dump_missing = model_missing.model_dump(by_alias=True, exclude_none=True)
    assert "variableOid" not in dump_missing


# Add more tests for edge cases, different variable types, etc.
