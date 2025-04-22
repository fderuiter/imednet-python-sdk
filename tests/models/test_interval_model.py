from datetime import datetime

import pytest
from pydantic import ValidationError

from imednet_sdk.models.interval import IntervalFormModel, IntervalModel

# Sample valid data based on docs/reference/intervals.md
VALID_INTERVAL_FORM_DATA = {"formId": 123, "formKey": "MY-FORM-KEY", "formName": "myFormName"}

VALID_INTERVAL_DATA = {
    "studyKey": "PHARMADEMO",
    "intervalId": 1,
    "intervalName": "Day 1",
    "intervalDescription": "Day 1",
    "intervalSequence": 110,
    "intervalGroupId": 10,
    "intervalGroupName": "ePRO",
    "disabled": True,  # Example has true, model default is false
    "dateCreated": "2024-11-04 16:03:19",
    "dateModified": "2024-11-04 16:03:20",
    "timeline": "Start Date End Date",
    "definedUsingInterval": "Baseline",
    "windowCalculationForm": "Procedure",
    "windowCalculationDate": "PROCDT",
    "actualDateForm": "Follow Up",
    "actualDate": "FUDT",
    "dueDateWillBeIn": 30,
    "negativeSlack": 7,
    "positiveSlack": 7,
    "eproGracePeriod": 2,
    "forms": [VALID_INTERVAL_FORM_DATA],
}

# --- IntervalFormModel Tests ---


def test_interval_form_model_validation():
    """Test successful validation of IntervalFormModel."""
    model = IntervalFormModel.model_validate(VALID_INTERVAL_FORM_DATA)
    assert model.formId == VALID_INTERVAL_FORM_DATA["formId"]
    assert model.formKey == VALID_INTERVAL_FORM_DATA["formKey"]
    assert model.formName == VALID_INTERVAL_FORM_DATA["formName"]


def test_interval_form_model_missing_required():
    """Test ValidationError for missing required field in IntervalFormModel."""
    invalid_data = VALID_INTERVAL_FORM_DATA.copy()
    del invalid_data["formId"]
    with pytest.raises(ValidationError):
        IntervalFormModel.model_validate(invalid_data)


def test_interval_form_model_invalid_type():
    """Test ValidationError for invalid type in IntervalFormModel."""
    invalid_data = VALID_INTERVAL_FORM_DATA.copy()
    invalid_data["formId"] = "not-an-int"
    with pytest.raises(ValidationError):
        IntervalFormModel.model_validate(invalid_data)


# --- IntervalModel Tests ---


def test_interval_model_validation():
    """Test successful validation of IntervalModel with valid data."""
    model = IntervalModel.model_validate(VALID_INTERVAL_DATA)

    assert model.studyKey == VALID_INTERVAL_DATA["studyKey"]
    assert model.intervalId == VALID_INTERVAL_DATA["intervalId"]
    assert model.intervalName == VALID_INTERVAL_DATA["intervalName"]
    assert model.intervalDescription == VALID_INTERVAL_DATA["intervalDescription"]
    assert model.intervalSequence == VALID_INTERVAL_DATA["intervalSequence"]
    assert model.intervalGroupId == VALID_INTERVAL_DATA["intervalGroupId"]
    assert model.intervalGroupName == VALID_INTERVAL_DATA["intervalGroupName"]
    assert model.disabled == VALID_INTERVAL_DATA["disabled"]
    assert isinstance(model.dateCreated, datetime)
    assert model.dateCreated == datetime(2024, 11, 4, 16, 3, 19)
    assert isinstance(model.dateModified, datetime)
    assert model.dateModified == datetime(2024, 11, 4, 16, 3, 20)
    assert model.timeline == VALID_INTERVAL_DATA["timeline"]
    assert model.definedUsingInterval == VALID_INTERVAL_DATA["definedUsingInterval"]
    assert model.windowCalculationForm == VALID_INTERVAL_DATA["windowCalculationForm"]
    assert model.windowCalculationDate == VALID_INTERVAL_DATA["windowCalculationDate"]
    assert model.actualDateForm == VALID_INTERVAL_DATA["actualDateForm"]
    assert model.actualDate == VALID_INTERVAL_DATA["actualDate"]
    assert model.dueDateWillBeIn == VALID_INTERVAL_DATA["dueDateWillBeIn"]
    assert model.negativeSlack == VALID_INTERVAL_DATA["negativeSlack"]
    assert model.positiveSlack == VALID_INTERVAL_DATA["positiveSlack"]
    assert model.eproGracePeriod == VALID_INTERVAL_DATA["eproGracePeriod"]

    assert isinstance(model.forms, list)
    assert len(model.forms) == 1
    assert isinstance(model.forms[0], IntervalFormModel)
    assert model.forms[0].formId == VALID_INTERVAL_FORM_DATA["formId"]


def test_interval_model_optional_fields_none():
    """Test validation when optional fields are explicitly None or missing."""
    data_with_none = VALID_INTERVAL_DATA.copy()
    data_with_none["intervalDescription"] = None
    data_with_none["definedUsingInterval"] = None
    data_with_none["windowCalculationForm"] = None
    data_with_none["windowCalculationDate"] = None
    data_with_none["actualDateForm"] = None
    data_with_none["actualDate"] = None
    data_with_none["dueDateWillBeIn"] = None
    data_with_none["negativeSlack"] = None
    data_with_none["positiveSlack"] = None
    data_with_none["eproGracePeriod"] = None

    model = IntervalModel.model_validate(data_with_none)
    assert model.intervalDescription is None
    assert model.definedUsingInterval is None
    assert model.windowCalculationForm is None
    assert model.windowCalculationDate is None
    assert model.actualDateForm is None
    assert model.actualDate is None
    assert model.dueDateWillBeIn is None
    assert model.negativeSlack is None
    assert model.positiveSlack is None
    assert model.eproGracePeriod is None

    data_missing_optionals = VALID_INTERVAL_DATA.copy()
    del data_missing_optionals["intervalDescription"]
    del data_missing_optionals["definedUsingInterval"]
    del data_missing_optionals["windowCalculationForm"]
    del data_missing_optionals["windowCalculationDate"]
    del data_missing_optionals["actualDateForm"]
    del data_missing_optionals["actualDate"]
    del data_missing_optionals["dueDateWillBeIn"]
    del data_missing_optionals["negativeSlack"]
    del data_missing_optionals["positiveSlack"]
    del data_missing_optionals["eproGracePeriod"]

    model_missing = IntervalModel.model_validate(data_missing_optionals)
    assert model_missing.intervalDescription is None  # Should default to None
    assert model_missing.definedUsingInterval is None
    assert model_missing.windowCalculationForm is None
    assert model_missing.windowCalculationDate is None
    assert model_missing.actualDateForm is None
    assert model_missing.actualDate is None
    assert model_missing.dueDateWillBeIn is None
    assert model_missing.negativeSlack is None
    assert model_missing.positiveSlack is None
    assert model_missing.eproGracePeriod is None


def test_interval_model_missing_required_field():
    """Test ValidationError is raised when a required field is missing."""
    invalid_data = VALID_INTERVAL_DATA.copy()
    del invalid_data["intervalName"]  # Remove a required field

    with pytest.raises(ValidationError) as excinfo:
        IntervalModel.model_validate(invalid_data)

    assert "intervalName" in str(excinfo.value)
    assert "Field required" in str(excinfo.value)


def test_interval_model_invalid_data_type():
    """Test ValidationError is raised for incorrect data types."""
    invalid_data = VALID_INTERVAL_DATA.copy()
    invalid_data["intervalSequence"] = "not-an-integer"

    with pytest.raises(ValidationError) as excinfo:
        IntervalModel.model_validate(invalid_data)

    assert "intervalSequence" in str(excinfo.value)
    assert "Input should be a valid integer" in str(excinfo.value)

    invalid_data_list = VALID_INTERVAL_DATA.copy()
    invalid_data_list["forms"] = "not-a-list"
    with pytest.raises(ValidationError) as excinfo_list:
        IntervalModel.model_validate(invalid_data_list)
    assert "forms" in str(excinfo_list.value)
    assert "Input should be a valid list" in str(excinfo_list.value)

    invalid_data_list_item = VALID_INTERVAL_DATA.copy()
    invalid_data_list_item["forms"] = [{"formId": "wrong_type"}]  # Invalid item in list
    with pytest.raises(ValidationError) as excinfo_item:
        IntervalModel.model_validate(invalid_data_list_item)
    assert "forms.0.formId" in str(excinfo_item.value)  # Check nested error


def test_interval_model_serialization():
    """Test serialization of the IntervalModel."""
    model = IntervalModel.model_validate(VALID_INTERVAL_DATA)
    dump = model.model_dump(by_alias=True)

    expected_data = VALID_INTERVAL_DATA.copy()
    # Adjust datetime serialization if needed
    # expected_data["dateCreated"] = model.dateCreated.isoformat()
    # expected_data["dateModified"] = model.dateModified.isoformat()

    # Check basic fields match
    for key, value in expected_data.items():
        # Exclude removed fields from the check
        if key not in ["dateCreated", "dateModified", "forms"]:
             assert dump[key] == value

    # Check datetime serialization
    assert dump["dateCreated"] == datetime(2024, 11, 4, 16, 3, 19)
    assert dump["dateModified"] == datetime(2024, 11, 4, 16, 3, 20)

    # Check nested model serialization
    assert isinstance(dump["forms"], list)
    assert len(dump["forms"]) == 1
    # Dump the nested model for comparison
    nested_model = IntervalFormModel.model_validate(VALID_INTERVAL_FORM_DATA)
    expected_nested_dump = nested_model.model_dump(by_alias=True)
    assert dump["forms"][0] == expected_nested_dump


# Add more tests for edge cases, specific timeline values, etc.
