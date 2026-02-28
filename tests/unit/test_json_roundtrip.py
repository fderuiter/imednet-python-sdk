import pytest

from imednet.models import (
    Coding,
    Form,
    Interval,
    Job,
    Query,
    Record,
    RecordRevision,
    Site,
    Study,
    Subject,
    User,
    Variable,
    Visit,
)
from imednet.testing import fake_data


@pytest.mark.parametrize(
    "cls,payload_func",
    [
        (Coding, fake_data.fake_coding),
        (Form, fake_data.fake_form),
        (Interval, fake_data.fake_interval),
        (Job, fake_data.fake_job),
        (Query, fake_data.fake_query),
        (Record, fake_data.fake_record),
        (RecordRevision, fake_data.fake_record_revision),
        (Site, fake_data.fake_site),
        (Study, fake_data.fake_study),
        (Subject, fake_data.fake_subject),
        (User, fake_data.fake_user),
        (Variable, fake_data.fake_variable),
        (Visit, fake_data.fake_visit),
    ],
)
def test_json_roundtrip(cls, payload_func):
    payload = payload_func()
    model = cls.from_json(payload)
    dumped = model.model_dump(by_alias=True)
    assert cls.from_json(dumped) == model


def test_fake_forms_for_cache():
    forms = fake_data.fake_forms_for_cache(num_forms=2, study_key="TEST-1")
    assert len(forms) == 2
    for form in forms:
        assert isinstance(form, Form)
        assert form.study_key == "TEST-1"


def test_fake_variables_for_cache():
    forms = fake_data.fake_forms_for_cache(num_forms=1)
    variables = fake_data.fake_variables_for_cache(forms, vars_per_form=2, study_key="TEST-1")
    assert len(variables) == 2
    for variable in variables:
        assert isinstance(variable, Variable)
        assert variable.study_key == "TEST-1"
        assert variable.form_id == forms[0].form_id
        assert variable.form_key == forms[0].form_key
        assert variable.form_name == forms[0].form_name
