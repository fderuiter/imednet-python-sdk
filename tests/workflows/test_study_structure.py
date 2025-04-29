from unittest.mock import Mock

import pytest
from imednet.core.exceptions import ImednetError
from imednet.models.forms import Form
from imednet.models.intervals import Interval
from imednet.models.study_structure import FormStructure, IntervalStructure, StudyStructure
from imednet.models.variables import Variable
from imednet.workflows.study_structure import get_study_structure


@pytest.fixture
def mock_sdk():
    sdk = Mock()
    return sdk


@pytest.fixture
def sample_data():
    # Create sample data for testing
    form1 = Mock(spec=Form)
    form1.form_id = 1
    form1.form_key = "FORM1"
    form1.form_name = "Form 1"
    form1.form_type = "CRF"
    form1.revision = 1
    form1.disabled = False
    form1.epro_form = False
    form1.allow_copy = True
    form1.date_created = "2024-01-01T00:00:00"
    form1.date_modified = "2024-01-02T00:00:00"
    form1.model_dump.return_value = {
        "formId": 1,
        "formKey": "FORM1",
        "formName": "Form 1",
        "formType": "CRF",
        "revision": 1,
        "disabled": False,
        "eproForm": False,
        "allowCopy": True,
        "dateCreated": "2024-01-01T00:00:00",
        "dateModified": "2024-01-02T00:00:00",
    }

    form2 = Mock(spec=Form)
    form2.form_id = 2
    form2.form_key = "FORM2"
    form2.form_name = "Form 2"
    form2.form_type = "CRF"
    form2.revision = 2
    form2.disabled = False
    form2.epro_form = True
    form2.allow_copy = False
    form2.date_created = "2024-01-03T00:00:00"
    form2.date_modified = "2024-01-04T00:00:00"
    form2.model_dump.return_value = {
        "formId": 2,
        "formKey": "FORM2",
        "formName": "Form 2",
        "formType": "CRF",
        "revision": 2,
        "disabled": False,
        "eproForm": True,
        "allowCopy": False,
        "dateCreated": "2024-01-03T00:00:00",
        "dateModified": "2024-01-04T00:00:00",
    }

    form_summary1 = Mock()
    form_summary1.form_id = 1

    form_summary2 = Mock()
    form_summary2.form_id = 2

    interval1 = Mock(spec=Interval)
    interval1.interval_id = 1
    interval1.label = "Interval 1"
    interval1.forms = [form_summary1, form_summary2]
    interval1.interval_name = "Interval 1"
    interval1.interval_sequence = 1
    interval1.interval_description = "Description"
    interval1.interval_group_name = "Group"
    interval1.disabled = False
    interval1.date_created = "2024-01-01T00:00:00"
    interval1.date_modified = "2024-01-02T00:00:00"
    interval1.model_dump.return_value = {
        "intervalId": 1,
        "intervalName": "Interval 1",
        "intervalSequence": 1,
        "intervalDescription": "Description",
        "intervalGroupName": "Group",
        "disabled": False,
        "dateCreated": "2024-01-01T00:00:00",
        "dateModified": "2024-01-02T00:00:00",
    }

    variable1 = Mock(spec=Variable)
    variable1.form_id = 1
    variable1.name = "var1"

    variable2 = Mock(spec=Variable)
    variable2.form_id = 2
    variable2.name = "var2"

    return {"forms": [form1, form2], "intervals": [interval1], "variables": [variable1, variable2]}


def test_get_study_structure_success(mock_sdk, sample_data):
    # Configure mocks
    mock_sdk.intervals.list.return_value = sample_data["intervals"]
    mock_sdk.forms.list.return_value = sample_data["forms"]
    mock_sdk.variables.list.return_value = sample_data["variables"]

    # Call the function
    result = get_study_structure(mock_sdk, "STUDY1")

    # Assertions
    assert isinstance(result, StudyStructure)
    assert result.study_key == "STUDY1"
    assert len(result.intervals) == 1
    assert isinstance(result.intervals[0], IntervalStructure)
    assert len(result.intervals[0].forms) == 2
    assert isinstance(result.intervals[0].forms[0], FormStructure)
    assert result.intervals[0].interval_id == 1

    # Verify API calls
    mock_sdk.intervals.list.assert_called_once_with("STUDY1")
    mock_sdk.forms.list.assert_called_once_with("STUDY1")
    mock_sdk.variables.list.assert_called_once_with("STUDY1")


def test_get_study_structure_empty_data(mock_sdk):
    # Configure mocks to return empty lists
    mock_sdk.intervals.list.return_value = []
    mock_sdk.forms.list.return_value = []
    mock_sdk.variables.list.return_value = []

    # Call the function
    result = get_study_structure(mock_sdk, "STUDY1")

    # Assertions
    assert isinstance(result, StudyStructure)
    assert result.study_key == "STUDY1"
    assert len(result.intervals) == 0


def test_get_study_structure_missing_form(mock_sdk, sample_data):
    # Setup interval with reference to non-existent form
    form_summary3 = Mock()
    form_summary3.form_id = 3  # Form with ID 3 doesn't exist

    sample_data["intervals"][0].forms.append(form_summary3)

    # Configure mocks
    mock_sdk.intervals.list.return_value = sample_data["intervals"]
    mock_sdk.forms.list.return_value = sample_data["forms"]
    mock_sdk.variables.list.return_value = sample_data["variables"]

    # Call the function
    result = get_study_structure(mock_sdk, "STUDY1")

    # Only existing forms should be included
    assert len(result.intervals[0].forms) == 2


def test_get_study_structure_api_error(mock_sdk):
    # Configure mock to raise an exception
    mock_sdk.intervals.list.side_effect = Exception("API Error")

    # Call the function and check that it raises the expected exception
    with pytest.raises(ImednetError) as excinfo:
        get_study_structure(mock_sdk, "STUDY1")

    assert "Failed to retrieve or process study structure" in str(excinfo.value)
