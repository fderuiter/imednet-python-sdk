from unittest.mock import MagicMock

import pytest

from imednet.core.exceptions import UnknownVariableTypeError, ValidationError
from imednet.models.variables import Variable
from imednet.validation.cache import (
    SchemaCache,
    SchemaValidator,
    _check_type,
    validate_record_data,
    validate_record_entry,
)


def _make_var(name: str, var_type: str = "integer") -> Variable:
    return Variable(variable_name=name, variable_type=var_type, form_id=1, form_key="F1")


def test_schema_cache_refresh() -> None:
    forms = MagicMock()
    variables = MagicMock()
    var = _make_var("age")
    variables.list.return_value = [var]

    cache = SchemaCache()
    cache.refresh(forms, variables, study_key="S")

    assert cache.form_key_from_id(1) == "F1"
    assert cache.variables_for_form("F1")["age"] is var
    forms.list.assert_not_called()
    variables.list.assert_called_once_with(study_key="S", refresh=True)


def test_check_type_int() -> None:
    var = _make_var("age")
    _check_type(var.variable_type, 5)
    with pytest.raises(ValidationError):
        _check_type(var.variable_type, "bad")


def test_check_type_other_types() -> None:
    bool_var = _make_var("flag", "boolean")
    float_var = _make_var("score", "float")
    str_var = _make_var("name", "string")

    _check_type(bool_var.variable_type, True)
    _check_type(float_var.variable_type, 1.5)
    _check_type(str_var.variable_type, "ok")

    with pytest.raises(ValidationError):
        _check_type(bool_var.variable_type, "nope")
    with pytest.raises(ValidationError):
        _check_type(float_var.variable_type, "nan")
    with pytest.raises(ValidationError):
        _check_type(str_var.variable_type, 123)


def test_check_type_unknown_type() -> None:
    with pytest.raises(UnknownVariableTypeError):
        _check_type("weird", "x")


def test_validate_record_data_errors() -> None:
    cache = SchemaCache()
    var = _make_var("age")
    # Bolt: Removed 'required' attribute injection as support was removed
    cache._form_variables["F1"] = {"age": var}

    with pytest.raises(ValidationError):
        validate_record_data(cache, "F1", {"other": 1})

    # Empty data is now valid if there are no required variables (or check is removed)
    validate_record_data(cache, "F1", {})

    with pytest.raises(ValidationError):
        validate_record_data(cache, "F1", {"age": "x"})


def test_validate_record_data_unknown_form() -> None:
    cache = SchemaCache()
    with pytest.raises(ValidationError, match="Unknown form BAD"):
        validate_record_data(cache, "BAD", {})


def test_schema_validator_batch_calls_validate_record() -> None:
    sdk = MagicMock()
    validator = SchemaValidator(sdk)
    validator.validate_record = MagicMock()  # type: ignore[assignment]

    validator.validate_batch("ST", [{"a": 1}, {"b": 2}])

    assert validator.validate_record.call_count == 2
    validator.validate_record.assert_any_call("ST", {"a": 1})
    validator.validate_record.assert_any_call("ST", {"b": 2})


def test_validate_record_entry_form_key_resolution() -> None:
    cache = SchemaCache()
    var = _make_var("age")
    cache._form_variables["F1"] = {"age": var}
    cache._form_id_to_key[1] = "F1"

    # Test resolution by formKey
    validate_record_entry(cache, {"formKey": "F1", "data": {"age": 5}})
    # Test resolution by form_key
    validate_record_entry(cache, {"form_key": "F1", "data": {"age": 5}})
    # Test resolution by formId
    validate_record_entry(cache, {"formId": 1, "data": {"age": 5}})
    # Test resolution by form_id
    validate_record_entry(cache, {"form_id": 1, "data": {"age": 5}})


def test_validate_record_entry_validation_error() -> None:
    cache = SchemaCache()
    var = _make_var("age")
    cache._form_variables["F1"] = {"age": var}

    with pytest.raises(ValidationError):
        validate_record_entry(cache, {"formKey": "F1", "data": {"age": "bad"}})


def test_validate_record_entry_unknown_form_ignored_if_no_id() -> None:
    """
    If no formKey/formId can be resolved, it should do nothing (or fail depending on logic).
    The current logic checks:
    fk = ...
    if not fk:
        fid = ...
        fk = schema.form_key_from_id(fid)
    if fk:
        validate...

    So if fk is None, it skips validation.
    """
    cache = SchemaCache()
    # No form identification -> no validation
    validate_record_entry(cache, {"data": {"whatever": 1}})
