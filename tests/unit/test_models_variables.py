from datetime import datetime

from imednet.models.variables import Variable


def test_variable_default_values():
    var = Variable()
    assert var.study_key == ""
    assert var.variable_id == 0
    assert var.variable_type == ""
    assert var.variable_name == ""
    assert var.sequence == 0
    assert var.revision == 0
    assert var.disabled is False
    assert isinstance(var.date_created, datetime)
    assert isinstance(var.date_modified, datetime)
    assert var.form_id == 0
    assert var.variable_oid is None
    assert var.deleted is False
    assert var.form_key == ""
    assert var.form_name == ""
    assert var.label == ""
    assert var.blinded is False


def test_variable_from_json():
    data = {
        "studyKey": "STUDY1",
        "variableId": 123,
        "variableType": "NUMBER",
        "variableName": "age",
        "sequence": 1,
        "revision": 2,
        "disabled": True,
        "dateCreated": "2023-01-01T00:00:00",
        "dateModified": "2023-01-02T00:00:00",
        "formId": 456,
        "variableOid": "V1",
        "deleted": True,
        "formKey": "FORM1",
        "formName": "Demographics",
        "label": "Age",
        "blinded": True,
    }

    var = Variable.from_json(data)

    assert var.study_key == "STUDY1"
    assert var.variable_id == 123
    assert var.variable_type == "NUMBER"
    assert var.variable_name == "age"
    assert var.sequence == 1
    assert var.revision == 2
    assert var.disabled is True
    assert var.date_created == datetime(2023, 1, 1, 0, 0)
    assert var.date_modified == datetime(2023, 1, 2, 0, 0)
    assert var.form_id == 456
    assert var.variable_oid == "V1"
    assert var.deleted is True
    assert var.form_key == "FORM1"
    assert var.form_name == "Demographics"
    assert var.label == "Age"
    assert var.blinded is True


def test_variable_field_validation():
    data = {
        "studyKey": None,
        "variableId": "123",  # String instead of int
        "disabled": "true",  # String instead of bool
        "dateCreated": "2023-01-01",  # Date string
    }

    var = Variable.from_json(data)

    assert var.study_key == ""  # Default for None string
    assert var.variable_id == 123  # Converted to int
    assert var.disabled is True  # Parsed bool from string
    assert var.date_created == datetime(2023, 1, 1)  # Parsed datetime
