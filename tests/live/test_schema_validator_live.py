import os
from typing import Iterator

import pytest

from imednet.core.exceptions import ValidationError
from imednet.sdk import ImednetSDK
from imednet.validation.cache import SchemaValidator

API_KEY = os.getenv("IMEDNET_API_KEY")
SECURITY_KEY = os.getenv("IMEDNET_SECURITY_KEY")
BASE_URL = os.getenv("IMEDNET_BASE_URL")
RUN_E2E = os.getenv("IMEDNET_RUN_E2E") == "1"

pytestmark = pytest.mark.skipif(
    not RUN_E2E or not (API_KEY and SECURITY_KEY),
    reason=(
        "Set IMEDNET_RUN_E2E=1 and provide IMEDNET_API_KEY/IMEDNET_SECURITY_KEY to run live tests"
    ),
)


@pytest.fixture(scope="session")
def sdk() -> Iterator[ImednetSDK]:
    with ImednetSDK(api_key=API_KEY, security_key=SECURITY_KEY, base_url=BASE_URL) as client:
        yield client


@pytest.fixture(scope="session")
def study_key(sdk: ImednetSDK) -> str:
    studies = sdk.studies.list()
    if not studies:
        pytest.skip("No studies available for live tests")
    return studies[0].study_key


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

    with pytest.raises(ValidationError):
        validator.validate_record(
            study_key, {"formKey": var.form_key, "data": {var.variable_name + "_x": 1}}
        )

    assert validator.schema.variables_for_form(var.form_key)


def test_validator_wrong_type(sdk: ImednetSDK, study_key: str) -> None:
    var = _get_first_variable(sdk, study_key)
    validator = SchemaValidator(sdk)
    validator.refresh(study_key)

    with pytest.raises(ValidationError):
        validator.validate_record(
            study_key,
            {"formKey": var.form_key, "data": {var.variable_name: _wrong_value(var.variable_type)}},
        )

    assert validator.schema.variables_for_form(var.form_key)
