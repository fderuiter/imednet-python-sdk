import pytest
from pydantic import ValidationError
from datetime import datetime

from imednet_sdk.models.form import FormModel

# Sample valid data based on docs/reference/forms.md
VALID_FORM_DATA = {
    "studyKey": "PHARMADEMO",
    "formId": 1,
    "formKey": "FORM_1",
    "formName": "Mock Form 1",
    "formType": "Subject",
    "revision": 1,
    "embeddedLog": False,
    "enforceOwnership": False,
    "userAgreement": False,
    "subjectRecordReport": False,
    "unscheduledVisit": False,
    "otherForms": False,
    "eproForm": False,
    "allowCopy": True,
    "disabled": False,
    "dateCreated": "2024-11-04 16:03:19",
    "dateModified": "2024-11-04 16:03:20"
}

def test_form_model_validation():
    """Test successful validation of FormModel with valid data."""
    model = FormModel.model_validate(VALID_FORM_DATA)

    assert model.studyKey == VALID_FORM_DATA["studyKey"]
    assert model.formId == VALID_FORM_DATA["formId"]
    assert model.formKey == VALID_FORM_DATA["formKey"]
    assert model.formName == VALID_FORM_DATA["formName"]
    assert model.formType == VALID_FORM_DATA["formType"]
    assert model.revision == VALID_FORM_DATA["revision"]
    assert model.embeddedLog == VALID_FORM_DATA["embeddedLog"]
    assert model.enforceOwnership == VALID_FORM_DATA["enforceOwnership"]
    assert model.userAgreement == VALID_FORM_DATA["userAgreement"]
    assert model.subjectRecordReport == VALID_FORM_DATA["subjectRecordReport"]
    assert model.unscheduledVisit == VALID_FORM_DATA["unscheduledVisit"]
    assert model.otherForms == VALID_FORM_DATA["otherForms"]
    assert model.eproForm == VALID_FORM_DATA["eproForm"]
    assert model.allowCopy == VALID_FORM_DATA["allowCopy"]
    assert model.disabled == VALID_FORM_DATA["disabled"]
    assert isinstance(model.dateCreated, datetime)
    assert model.dateCreated == datetime(2024, 11, 4, 16, 3, 19)
    assert isinstance(model.dateModified, datetime)
    assert model.dateModified == datetime(2024, 11, 4, 16, 3, 20)

def test_form_model_missing_required_field():
    """Test ValidationError is raised when a required field is missing."""
    invalid_data = VALID_FORM_DATA.copy()
    del invalid_data["formName"] # Remove a required field

    with pytest.raises(ValidationError) as excinfo:
        FormModel.model_validate(invalid_data)

    assert "formName" in str(excinfo.value)
    assert "Field required" in str(excinfo.value)

def test_form_model_invalid_data_type():
    """Test ValidationError is raised for incorrect data types."""
    invalid_data = VALID_FORM_DATA.copy()
    invalid_data["formId"] = "not-an-integer" # Incorrect type

    with pytest.raises(ValidationError) as excinfo:
        FormModel.model_validate(invalid_data)

    assert "formId" in str(excinfo.value)
    assert "Input should be a valid integer" in str(excinfo.value)

    invalid_data_bool = VALID_FORM_DATA.copy()
    invalid_data_bool["disabled"] = "not-a-boolean"
    with pytest.raises(ValidationError) as excinfo_bool:
        FormModel.model_validate(invalid_data_bool)

    assert "disabled" in str(excinfo_bool.value)
    assert "Input should be a valid boolean" in str(excinfo_bool.value)

def test_form_model_serialization():
    """Test serialization of the FormModel."""
    model = FormModel.model_validate(VALID_FORM_DATA)
    dump = model.model_dump(by_alias=True)

    expected_data = VALID_FORM_DATA.copy()
    # Adjust datetime serialization if needed based on Pydantic defaults
    # expected_data["dateCreated"] = model.dateCreated.isoformat()
    # expected_data["dateModified"] = model.dateModified.isoformat()

    # Check basic fields match
    for key, value in expected_data.items():
        if key not in ["dateCreated", "dateModified"]:
            assert dump[key] == value

    # Check datetime serialization
    assert dump["dateCreated"] == datetime(2024, 11, 4, 16, 3, 19)
    assert dump["dateModified"] == datetime(2024, 11, 4, 16, 3, 20)

# Add more tests for edge cases, default values, etc.
