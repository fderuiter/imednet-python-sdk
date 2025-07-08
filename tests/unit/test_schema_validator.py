from unittest.mock import MagicMock

import pytest

from imednet.core.exceptions import ValidationError
from imednet.models.variables import Variable
from imednet.validation.cache import SchemaValidator


def _build_sdk(variable: Variable) -> MagicMock:
    sdk = MagicMock()
    sdk.variables.list.return_value = [variable]
    return sdk


def test_validate_record_unknown_variable() -> None:
    var = Variable(variable_name="age", variable_type="integer", form_id=1, form_key="F1")
    sdk = _build_sdk(var)
    validator = SchemaValidator(sdk)

    with pytest.raises(ValidationError):
        validator.validate_record("STUDY", {"formKey": "F1", "data": {"bad": 1}})

    sdk.variables.list.assert_called_once_with(study_key="STUDY", refresh=True)


def test_validate_record_wrong_type() -> None:
    var = Variable(variable_name="age", variable_type="integer", form_id=1, form_key="F1")
    sdk = _build_sdk(var)
    validator = SchemaValidator(sdk)

    with pytest.raises(ValidationError):
        validator.validate_record("STUDY", {"formKey": "F1", "data": {"age": "x"}})

    sdk.variables.list.assert_called_once_with(study_key="STUDY", refresh=True)


def test_refresh_called_when_form_not_cached() -> None:
    var = Variable(variable_name="age", variable_type="integer", form_id=1, form_key="F1")
    sdk = _build_sdk(var)
    validator = SchemaValidator(sdk)
    validator.refresh = MagicMock(wraps=validator.refresh)  # type: ignore[assignment]

    validator.validate_record("STUDY", {"formKey": "F1", "data": {"age": 1}})

    validator.refresh.assert_called_once_with("STUDY")
    sdk.variables.list.assert_called_once_with(study_key="STUDY", refresh=True)


def test_validate_record_cached(monkeypatch) -> None:
    var = Variable(variable_name="age", variable_type="integer", form_id=1, form_key="F1")
    sdk = _build_sdk(var)
    validator = SchemaValidator(sdk)
    validator.schema._form_variables["F1"] = {"age": var}

    validator.validate_record("STUDY", {"formKey": "F1", "data": {"age": 1}})

    sdk.variables.list.assert_not_called()
