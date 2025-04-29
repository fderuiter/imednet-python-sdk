from datetime import datetime

import pytest
from imednet.models.forms import Form
from imednet.models.intervals import Interval
from imednet.models.study_structure import FormStructure, IntervalStructure, StudyStructure
from imednet.models.variables import Variable


@pytest.fixture
def sample_variable():
    return Variable(
        variableId=1,
        variableKey="test_var",
        variableName="Test Variable",
        variableType="text",
        dateCreated=datetime.now(),
        dateModified=datetime.now(),
    )


@pytest.fixture
def sample_form():
    return Form(
        formId=1,
        formKey="test_form",
        formName="Test Form",
        formType="standard",
        revision=1,
        disabled=False,
        eproForm=False,
        allowCopy=True,
        dateCreated=datetime.now(),
        dateModified=datetime.now(),
    )


@pytest.fixture
def sample_interval():
    return Interval(
        intervalId=1,
        intervalName="Test Interval",
        intervalSequence=1,
        intervalDescription="Test Description",
        intervalGroupName="Test Group",
        disabled=False,
        dateCreated=datetime.now(),
        dateModified=datetime.now(),
        forms=[],
    )


def test_form_structure_creation(sample_form, sample_variable):
    variables = [sample_variable]
    form_structure = FormStructure.from_form(sample_form, variables)

    assert form_structure.form_id == sample_form.form_id
    assert form_structure.form_key == sample_form.form_key
    assert form_structure.variables == variables


def test_interval_structure_creation(sample_interval, sample_form, sample_variable):
    form_structure = FormStructure.from_form(sample_form, [sample_variable])
    interval_structure = IntervalStructure.from_interval(sample_interval, [form_structure])

    assert interval_structure.interval_id == sample_interval.interval_id
    assert interval_structure.interval_name == sample_interval.interval_name
    assert len(interval_structure.forms) == 1
    assert interval_structure.forms[0] == form_structure


def test_study_structure_creation():
    study = StudyStructure(studyKey="TEST01")
    assert study.study_key == "TEST01"
    assert study.intervals == []


def test_model_aliases():
    study = StudyStructure(studyKey="TEST01")
    data = study.model_dump(by_alias=True)
    assert "studyKey" in data
    assert data["studyKey"] == "TEST01"
