from datetime import datetime, timezone

from imednet.models.forms import Form

SAMPLE_FORM_DATA = {
    "studyKey": "STUDY1",
    "formId": 101,
    "formKey": "FORM_A",
    "formName": "Form A",
    "formType": "CRF",
    "revision": 2,
    "embeddedLog": True,
    "enforceOwnership": False,
    "userAgreement": True,
    "subjectRecordReport": False,
    "unscheduledVisit": True,
    "otherForms": False,
    "eproForm": True,
    "allowCopy": False,
    "disabled": False,
    "dateCreated": "2023-10-27T10:00:00Z",
    "dateModified": "2023-10-28T11:00:00Z",
}


def test_form_creation():
    form = Form.model_validate(SAMPLE_FORM_DATA)
    assert form.study_key == "STUDY1"
    assert form.form_id == 101
    assert form.form_key == "FORM_A"
    assert form.form_name == "Form A"
    assert form.form_type == "CRF"
    assert form.revision == 2
    assert form.embedded_log is True
    assert form.enforce_ownership is False
    assert form.user_agreement is True
    assert form.subject_record_report is False
    assert form.unscheduled_visit is True
    assert form.other_forms is False
    assert form.epro_form is True
    assert form.allow_copy is False
    assert form.disabled is False
    assert form.date_created == datetime(2023, 10, 27, 10, 0, 0, tzinfo=timezone.utc)
    assert form.date_modified == datetime(2023, 10, 28, 11, 0, 0, tzinfo=timezone.utc)


def test_form_defaults():
    form = Form.model_validate({})
    assert form.study_key == ""
    assert form.form_id == 0
    assert form.form_key == ""
    assert form.form_name == ""
    assert form.form_type == ""
    assert form.revision == 0
    assert form.embedded_log is False
    assert form.enforce_ownership is False
    assert form.user_agreement is False
    assert form.subject_record_report is False
    assert form.unscheduled_visit is False
    assert form.other_forms is False
    assert form.epro_form is False
    assert form.allow_copy is False
    assert form.disabled is False
    assert isinstance(form.date_created, datetime)
    assert isinstance(form.date_modified, datetime)


def test_form_str_int_bool_parsing():
    data = {
        "studyKey": None,
        "formId": "123",
        "formKey": None,
        "formName": None,
        "formType": None,
        "revision": "5",
        "embeddedLog": "true",
        "enforceOwnership": "false",
        "userAgreement": 1,
        "subjectRecordReport": 0,
        "unscheduledVisit": "True",
        "otherForms": "False",
        "eproForm": "yes",
        "allowCopy": "no",
        "disabled": None,
        "dateCreated": "2024-01-01T12:00:00Z",
        "dateModified": "2024-01-02T13:00:00Z",
    }
    form = Form.model_validate(data)
    assert form.study_key == ""
    assert form.form_id == 123
    assert form.form_key == ""
    assert form.form_name == ""
    assert form.form_type == ""
    assert form.revision == 5
    assert form.embedded_log is True
    assert form.enforce_ownership is False
    assert form.user_agreement is True
    assert form.subject_record_report is False
    assert form.unscheduled_visit is True
    assert form.other_forms is False
    assert form.epro_form is True
    assert form.allow_copy is False
    assert form.disabled is False
    assert form.date_created == datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
    assert form.date_modified == datetime(2024, 1, 2, 13, 0, 0, tzinfo=timezone.utc)
