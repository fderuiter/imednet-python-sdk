"""Test Fake Data module."""

from types import SimpleNamespace
from typing import Any, cast

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
from imednet.validation.cache import SchemaCache, validate_record_data


def test_fake_subject_parses() -> None:
    """Test the test fake subject parses functionality."""
    data = fake_data.fake_subject()
    obj = Subject.from_json(data)
    assert isinstance(obj, Subject)


def test_fake_site_parses() -> None:
    """Test the test fake site parses functionality."""
    data = fake_data.fake_site()
    obj = Site.from_json(data)
    assert isinstance(obj, Site)


def test_fake_interval_parses() -> None:
    """Test the test fake interval parses functionality."""
    data = fake_data.fake_interval()
    obj = Interval.from_json(data)
    assert isinstance(obj, Interval)


def test_fake_query_parses() -> None:
    """Test the test fake query parses functionality."""
    data = fake_data.fake_query()
    obj = Query.from_json(data)
    assert isinstance(obj, Query)


def test_fake_record_parses() -> None:
    """Test the test fake record parses functionality."""
    data = fake_data.fake_record()
    obj = Record.from_json(data)
    assert isinstance(obj, Record)


def test_fake_record_with_schema() -> None:
    """Test the test fake record with schema functionality."""
    cache = SchemaCache()
    var = Variable(variable_name="age", variable_type="integer", form_id=1, form_key="F1")
    object.__setattr__(var, "required", True)
    cache._form_variables = {"F1": {"age": var}}
    cache._form_id_to_key = {1: "F1"}

    data = fake_data.fake_record(cache)
    obj = Record.from_json(data)
    assert obj.form_key == "F1"
    assert isinstance(obj.record_data.get("age"), int)


def test_fake_form_parses() -> None:
    """Test the test fake form parses functionality."""
    data = fake_data.fake_form()
    obj = Form.from_json(data)
    assert isinstance(obj, Form)


def test_fake_variable_parses() -> None:
    """Test the test fake variable parses functionality."""
    data = fake_data.fake_variable()
    obj = Variable.from_json(data)
    assert isinstance(obj, Variable)


def test_fake_visit_parses() -> None:
    """Test the test fake visit parses functionality."""
    data = fake_data.fake_visit()
    obj = Visit.from_json(data)
    assert isinstance(obj, Visit)


def test_fake_coding_parses() -> None:
    """Test the test fake coding parses functionality."""
    data = fake_data.fake_coding()
    obj = Coding.from_json(data)
    assert isinstance(obj, Coding)


def test_fake_record_revision_parses() -> None:
    """Test the test fake record revision parses functionality."""
    data = fake_data.fake_record_revision()
    obj = RecordRevision.from_json(data)
    assert isinstance(obj, RecordRevision)


def test_fake_study_parses() -> None:
    """Test the test fake study parses functionality."""
    data = fake_data.fake_study()
    obj = Study.model_validate(data)
    assert isinstance(obj, Study)


def test_fake_job_parses() -> None:
    """Test the test fake job parses functionality."""
    data = fake_data.fake_job()
    obj = Job.from_json(data)
    assert isinstance(obj, Job)


def test_fake_user_parses() -> None:
    """Test the test fake user parses functionality."""
    data = fake_data.fake_user()
    obj = User.from_json(data)
    assert isinstance(obj, User)


def test_fake_forms_for_cache_returns_forms() -> None:
    """Test the test fake forms for cache returns forms functionality."""
    forms = fake_data.fake_forms_for_cache(2, study_key="S")
    assert len(forms) == 2
    assert all(isinstance(f, Form) for f in forms)
    assert {f.study_key for f in forms} == {"S"}


def test_fake_variables_for_cache_and_schema_refresh() -> None:
    """Test the test fake variables for cache and schema refresh functionality."""
    forms = fake_data.fake_forms_for_cache(1)
    variables = fake_data.fake_variables_for_cache(forms, vars_per_form=1)

    forms_ep = SimpleNamespace(list=lambda **_: forms)

    def list_vars(*_, form_id=None, **__):
        """Test the list vars functionality."""
        return [v for v in variables if form_id is None or v.form_id == form_id]

    vars_ep = SimpleNamespace(list=list_vars)

    cache = SchemaCache()
    cache.refresh(cast(Any, forms_ep), cast(Any, vars_ep), study_key="X")

    form = forms[0]
    var = variables[0]

    assert cache.form_key_from_id(form.form_id) == form.form_key
    assert cache.variables_for_form(form.form_key)[var.variable_name] is var


def test_fake_forms_for_cache_from_json() -> None:
    """Test the test fake forms for cache from json functionality."""
    forms = fake_data.fake_forms_for_cache(2)
    for form in forms:
        parsed = Form.from_json(form.model_dump(by_alias=True))
        assert isinstance(parsed, Form)


def test_fake_variables_for_cache_from_json() -> None:
    """Test the test fake variables for cache from json functionality."""
    forms = fake_data.fake_forms_for_cache(1)
    variables = fake_data.fake_variables_for_cache(forms, vars_per_form=2)
    for var in variables:
        parsed = Variable.from_json(var.model_dump(by_alias=True))
        assert isinstance(parsed, Variable)


def test_validate_record_data_with_cached_schema() -> None:
    """Test the test validate record data with cached schema functionality."""
    forms = fake_data.fake_forms_for_cache(1)
    variables = fake_data.fake_variables_for_cache(forms, vars_per_form=1)
    variables[0].variable_type = "integer"

    forms_ep = SimpleNamespace(list=lambda **_: forms)

    def list_vars(*_, form_id=None, **__):
        """Test the list vars functionality."""
        return [v for v in variables if form_id is None or v.form_id == form_id]

    vars_ep = SimpleNamespace(list=list_vars)

    cache = SchemaCache()
    cache.refresh(cast(Any, forms_ep), cast(Any, vars_ep), study_key="X")

    record_data = fake_data.fake_record(cache)

    validate_record_data(cache, record_data["formKey"], record_data["recordData"])  # type: ignore[arg-type]
