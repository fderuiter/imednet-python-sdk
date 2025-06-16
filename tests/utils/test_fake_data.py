import imednet.testing.fake_data as fake_data
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


def test_fake_subject_parses() -> None:
    data = fake_data.fake_subject()
    obj = Subject.from_json(data)
    assert isinstance(obj, Subject)


def test_fake_site_parses() -> None:
    data = fake_data.fake_site()
    obj = Site.from_json(data)
    assert isinstance(obj, Site)


def test_fake_interval_parses() -> None:
    data = fake_data.fake_interval()
    obj = Interval.from_json(data)
    assert isinstance(obj, Interval)


def test_fake_query_parses() -> None:
    data = fake_data.fake_query()
    obj = Query.from_json(data)
    assert isinstance(obj, Query)


def test_fake_record_parses() -> None:
    data = fake_data.fake_record()
    obj = Record.from_json(data)
    assert isinstance(obj, Record)


def test_fake_form_parses() -> None:
    data = fake_data.fake_form()
    obj = Form.from_json(data)
    assert isinstance(obj, Form)


def test_fake_variable_parses() -> None:
    data = fake_data.fake_variable()
    obj = Variable.from_json(data)
    assert isinstance(obj, Variable)


def test_fake_visit_parses() -> None:
    data = fake_data.fake_visit()
    obj = Visit.from_json(data)
    assert isinstance(obj, Visit)


def test_fake_coding_parses() -> None:
    data = fake_data.fake_coding()
    obj = Coding.from_json(data)
    assert isinstance(obj, Coding)


def test_fake_record_revision_parses() -> None:
    data = fake_data.fake_record_revision()
    obj = RecordRevision.from_json(data)
    assert isinstance(obj, RecordRevision)


def test_fake_study_parses() -> None:
    data = fake_data.fake_study()
    obj = Study.model_validate(data)
    assert isinstance(obj, Study)


def test_fake_job_parses() -> None:
    data = fake_data.fake_job()
    obj = Job.from_json(data)
    assert isinstance(obj, Job)


def test_fake_user_parses() -> None:
    data = fake_data.fake_user()
    obj = User.from_json(data)
    assert isinstance(obj, User)
