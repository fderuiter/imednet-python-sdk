from datetime import datetime
from typing import Any, Union, get_args, get_origin

import pytest
from pydantic import BaseModel, ValidationError

import imednet.models as models


def _build_value(annotation: Any) -> Any:
    origin = get_origin(annotation)
    if origin is list:
        sub = get_args(annotation)[0]
        return [_build_value(sub)]
    if origin is dict:
        return {"k": "v"}
    if origin is Union:
        args = [a for a in get_args(annotation) if a is not type(None)]
        if not args:
            return None
        sub = args[0]
        if sub is datetime:
            return ""
        return _build_value(sub)
    if isinstance(annotation, type) and issubclass(annotation, BaseModel):
        return _build_sample_data(annotation)
    if annotation is int:
        return "1"
    if annotation is bool:
        return "true"
    if annotation is datetime:
        return "2024-01-01T00:00:00Z"
    return "value"


def _build_sample_data(cls: type[BaseModel]) -> Any:
    if getattr(cls, "__pydantic_root_model__", False):
        return {"foo": "bar"}
    data = {}
    for name, field in cls.model_fields.items():
        data[field.alias or name] = _build_value(field.annotation)
    return data


MODEL_CLASSES = [
    cls
    for cls in (v for v in vars(models).values() if isinstance(v, type))
    if issubclass(cls, BaseModel) and cls.__module__.startswith("imednet.models")
]


@pytest.mark.parametrize("model_cls", MODEL_CLASSES)
def test_model_instantiation_and_dump(model_cls: type[BaseModel]) -> None:
    sample = _build_sample_data(model_cls)
    model = model_cls.model_validate(sample)
    dumped = model.model_dump(by_alias=True)
    if not getattr(model_cls, "__pydantic_root_model__", False):
        for name, field in model_cls.model_fields.items():
            alias = field.alias or name
            assert alias in dumped
    else:
        assert dumped == sample


@pytest.mark.parametrize("model_cls", MODEL_CLASSES)
def test_missing_required_fields(model_cls: type[BaseModel]) -> None:
    if getattr(model_cls, "__pydantic_root_model__", False):
        model_cls.model_validate({})
        return
    required = [f for f in model_cls.model_fields.values() if f.is_required()]
    if required:
        with pytest.raises(ValidationError):
            model_cls.model_validate({})
    else:
        instance = model_cls.model_validate({})
        assert isinstance(instance, model_cls)


@pytest.mark.parametrize("model_cls", MODEL_CLASSES)
def test_invalid_int_defaults(model_cls: type[BaseModel]) -> None:
    if getattr(model_cls, "__pydantic_root_model__", False):
        pytest.skip("root model")
    int_field_item = next(
        (
            (name, field)
            for name, field in model_cls.model_fields.items()
            if field.annotation is int and not field.is_required()
        ),
        None,
    )
    if not int_field_item:
        pytest.skip("no int field")
    name, field = int_field_item
    data = _build_sample_data(model_cls)
    data[field.alias or name] = "notanint"
    model = model_cls.model_validate(data)
    assert getattr(model, name) == 0


def test_job_properties() -> None:
    from imednet.models.jobs import Job

    job_completed = Job(batchId="1", state="COMPLETED")
    assert job_completed.is_terminal
    assert job_completed.is_successful
    assert not job_completed.is_failed

    job_failed = Job(batchId="1", state="FAILED")
    assert job_failed.is_terminal
    assert not job_failed.is_successful
    assert job_failed.is_failed

    job_cancelled = Job(batchId="1", state="CANCELLED")
    assert job_cancelled.is_terminal
    assert not job_cancelled.is_successful
    assert job_cancelled.is_failed

    job_processing = Job(batchId="1", state="PROCESSING")
    assert not job_processing.is_terminal
    assert not job_processing.is_successful
    assert not job_processing.is_failed

    job_success = Job(batchId="1", state="SUCCESS")
    assert job_success.is_terminal
    assert job_success.is_successful
    assert not job_success.is_failed


def test_job_status_progress_parsing() -> None:
    from imednet.models.jobs import JobStatus

    js_valid = JobStatus(batchId="1", state="PROCESSING", progress="50")
    assert js_valid.progress == 50

    js_invalid = JobStatus(batchId="1", state="PROCESSING", progress="invalid")
    assert js_invalid.progress == 0

    js_none = JobStatus(batchId="1", state="PROCESSING", progress=None)
    assert js_none.progress == 0


def test_study_structure_methods() -> None:
    from datetime import datetime

    from imednet.models.forms import Form
    from imednet.models.intervals import Interval
    from imednet.models.study_structure import FormStructure, IntervalStructure

    form = Form(
        formId=1,
        formKey="TEST_FORM",
        formName="Test Form",
        formType="CRF",
        revision=1,
        disabled=False,
        eproForm=False,
        allowCopy=True,
        dateCreated=datetime(2024, 1, 1),
        dateModified=datetime(2024, 1, 2),
    )

    form_struct = FormStructure.from_form(form, variables=[])
    assert form_struct.form_id == 1
    assert form_struct.form_key == "TEST_FORM"
    assert len(form_struct.variables) == 0

    interval = Interval(
        intervalId=10,
        intervalName="Baseline",
        intervalSequence=1,
        intervalDescription="Baseline Visit",
        intervalGroupName="Visits",
        disabled=False,
        dateCreated=datetime(2024, 1, 1),
        dateModified=datetime(2024, 1, 2),
        forms=[{"formId": 1, "formKey": "TEST_FORM", "formName": "Test Form"}],
    )

    interval_struct = IntervalStructure.from_interval(interval, forms=[form_struct])
    assert interval_struct.interval_id == 10
    assert interval_struct.interval_name == "Baseline"
    assert len(interval_struct.forms) == 1
    assert interval_struct.forms[0].form_id == 1


def test_visit_clean_empty_dates() -> None:
    from imednet.models.visits import Visit

    # Valid date
    v1 = Visit(startDate="2024-01-01T00:00:00Z")
    assert v1.start_date is not None

    # Empty date string
    v2 = Visit(startDate="")
    assert v2.start_date is None

    # None date
    v3 = Visit(startDate=None)
    assert v3.start_date is None


def test_study_structure_study() -> None:
    from imednet.models.study_structure import StudyStructure

    study = StudyStructure(studyKey="ST1", intervals=[])
    assert study.study_key == "ST1"
