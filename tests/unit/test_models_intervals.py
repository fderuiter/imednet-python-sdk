from datetime import datetime

from imednet.models.intervals import FormSummary, Interval


def test_form_summary_from_json():
    data = {"formId": 123, "formKey": "test_key", "formName": "Test Form"}
    form = FormSummary.from_json(data)
    assert form.form_id == 123
    assert form.form_key == "test_key"
    assert form.form_name == "Test Form"


def test_form_summary_default_values():
    form = FormSummary()
    assert form.form_id == 0
    assert form.form_key == ""
    assert form.form_name == ""


def test_interval_from_json():
    data = {
        "studyKey": "study1",
        "intervalId": 1,
        "intervalName": "Test Interval",
        "intervalDescription": "Description",
        "intervalSequence": 2,
        "intervalGroupId": 3,
        "intervalGroupName": "Group 1",
        "disabled": True,
        "dateCreated": "2023-01-01T00:00:00",
        "dateModified": "2023-01-02T00:00:00",
        "timeline": "timeline1",
        "definedUsingInterval": "interval1",
        "windowCalculationForm": "form1",
        "windowCalculationDate": "date1",
        "actualDateForm": "form2",
        "actualDate": "date2",
        "dueDateWillBeIn": 5,
        "negativeSlack": 1,
        "positiveSlack": 2,
        "eproGracePeriod": 3,
        "forms": [{"formId": 1, "formKey": "key1", "formName": "name1"}],
    }
    interval = Interval.from_json(data)

    assert interval.study_key == "study1"
    assert interval.interval_id == 1
    assert interval.interval_name == "Test Interval"
    assert interval.disabled is True
    assert isinstance(interval.date_created, datetime)
    assert isinstance(interval.date_modified, datetime)
    assert len(interval.forms) == 1
    assert interval.forms[0].form_id == 1


def test_interval_default_values():
    interval = Interval()
    assert interval.study_key == ""
    assert interval.interval_id == 0
    assert interval.interval_name == ""
    assert interval.disabled is False
    assert isinstance(interval.date_created, datetime)
    assert isinstance(interval.date_modified, datetime)
    assert interval.forms == []


def test_interval_alias_field_names():
    data = {"study_key": "study1", "interval_id": 1, "forms": []}
    interval = Interval(**data)
    assert interval.study_key == "study1"
    assert interval.interval_id == 1
