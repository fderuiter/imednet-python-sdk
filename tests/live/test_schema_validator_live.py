import pytest

from imednet.core.exceptions import ValidationError
from imednet.sdk import ImednetSDK
from imednet.validation.cache import SchemaValidator


def _get_first_variable(sdk: ImednetSDK, study_key: str):
    variables = sdk.variables.list(study_key=study_key)
    if not variables:
        pytest.skip("No variables available for live tests")
    return variables[0]


def _wrong_value(var_type: str):
    t = var_type.lower()
    if t in {"text", "string"}:
        return 1
    return "bad"


def test_validator_unknown_variable(sdk: ImednetSDK, study_key: str) -> None:
    var = _get_first_variable(sdk, study_key)
    validator = SchemaValidator(sdk)
    validator.refresh(study_key)

    # Ensure schema contains variables for the form; an empty schema would cause
    # false negatives when validating.
    assert validator.schema.variables_for_form(var.form_key)

    with pytest.raises(ValidationError):
        validator.validate_record(
            study_key, {"formKey": var.form_key, "data": {var.variable_name + "_x": 1}}
        )


def test_validator_wrong_type(sdk: ImednetSDK, study_key: str) -> None:
    var = _get_first_variable(sdk, study_key)
    validator = SchemaValidator(sdk)
    validator.refresh(study_key)

    # The validator requires a populated schema; without this check the test
    # could pass incorrectly if the form variables are missing.
    assert validator.schema.variables_for_form(var.form_key)

    with pytest.raises(ValidationError):
        validator.validate_record(
            study_key,
            {"formKey": var.form_key, "data": {var.variable_name: _wrong_value(var.variable_type)}},
        )
