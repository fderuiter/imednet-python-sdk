import logging
import os
from typing import Any, AsyncIterator, Callable, Iterator

import pytest

from imednet.sdk import AsyncImednetSDK, ImednetSDK
from imednet.testing import typed_values
from tests.live.helpers import get_form_key, get_study_key

API_KEY = os.getenv("IMEDNET_API_KEY")
SECURITY_KEY = os.getenv("IMEDNET_SECURITY_KEY")
BASE_URL = os.getenv("IMEDNET_BASE_URL")
RUN_E2E = os.getenv("IMEDNET_RUN_E2E") == "1"

logger = logging.getLogger(__name__)


def _typed_value(var_type: str) -> Any:
    """Return a deterministic example value for ``var_type``."""

    val = typed_values.value_for(var_type)
    if val is None:
        raise ValueError(f"No typed value for {var_type!r}")
    return val


@pytest.fixture(scope="session", autouse=True)
def _check_live_env() -> None:
    if not RUN_E2E or not (API_KEY and SECURITY_KEY):
        pytest.skip(
            "Set IMEDNET_RUN_E2E=1 and provide IMEDNET_API_KEY/IMEDNET_SECURITY_KEY "
            "to run live tests"
        )
    logger.info("Live test environment configured")


@pytest.fixture(scope="session")
def sdk() -> Iterator[ImednetSDK]:
    with ImednetSDK(api_key=API_KEY, security_key=SECURITY_KEY, base_url=BASE_URL) as client:
        yield client


@pytest.fixture(scope="session")
async def async_sdk() -> AsyncIterator[AsyncImednetSDK]:
    """
    Provides a session-scoped asynchronous ImednetSDK client.
    """
    client = AsyncImednetSDK(api_key=API_KEY, security_key=SECURITY_KEY, base_url=BASE_URL)
    yield client
    await client.aclose()


@pytest.fixture(scope="session")
def study_key(sdk: ImednetSDK) -> str:
    return get_study_key(sdk)


@pytest.fixture(scope="session")
def first_form_key(sdk: ImednetSDK, study_key: str) -> str:
    return get_form_key(sdk, study_key)


@pytest.fixture(scope="session")
def first_site_name(sdk: ImednetSDK, study_key: str) -> str:
    sites = sdk.sites.list(study_key=study_key)
    if not sites:
        pytest.skip(f"No sites available for study {study_key}")
    return sites[0].site_name


@pytest.fixture(scope="session")
def first_subject_key(sdk: ImednetSDK, study_key: str) -> str:
    subjects = sdk.subjects.list(study_key=study_key)
    if not subjects:
        pytest.skip(f"No subjects available for study {study_key}")
    return subjects[0].subject_key


@pytest.fixture(scope="session")
def first_interval_name(sdk: ImednetSDK, study_key: str) -> str:
    intervals = sdk.intervals.list(study_key=study_key)
    if not intervals:
        pytest.skip(f"No intervals available for study {study_key}")
    return intervals[0].interval_name


@pytest.fixture(scope="session")
def generated_batch_id(sdk: ImednetSDK, study_key: str, first_form_key: str) -> str:
    variables = sdk.variables.list(study_key=study_key, formKey=first_form_key)
    if not variables:
        pytest.skip(f"No variables available for form {first_form_key}")

    data: dict[str, Any] = {}
    for var in variables:
        required = any(
            getattr(var, attr, False) for attr in ("is_required", "required", "mandatory")
        )
        if required:
            data[var.variable_name] = _typed_value(var.variable_type)
    if not data:
        var = variables[0]
        data[var.variable_name] = _typed_value(var.variable_type)

    record = {"formKey": first_form_key, "data": data}
    job = sdk.records.create(study_key, [record])
    return job.batch_id


@pytest.fixture(scope="session")
def typed_record(
    sdk: ImednetSDK,
    study_key: str,
    first_form_key: str,
) -> Callable[..., dict[str, Any]]:
    variables = sdk.variables.list(study_key=study_key, formKey=first_form_key)
    if not variables:
        pytest.skip(f"No variables available for form {first_form_key}")

    selected: dict[str, Any] = {}
    for var in variables:
        var_type = typed_values.canonical_type(var.variable_type)
        if var_type and var_type not in selected:
            selected[var_type] = var

    data = {
        var.variable_name: typed_values.value_for(var.variable_type) for var in selected.values()
    }

    def build(
        *,
        site_name: str | None = None,
        subject_key: str | None = None,
        interval_name: str | None = None,
    ) -> dict[str, Any]:
        record: dict[str, Any] = {"formKey": first_form_key, "data": data}
        if site_name is not None:
            record["siteName"] = site_name
        if subject_key is not None:
            record["subjectKey"] = subject_key
        if interval_name is not None:
            record["intervalName"] = interval_name
        return record

    return build


@pytest.fixture
def record_payload(
    request: pytest.FixtureRequest,
    typed_record: Callable[..., dict[str, Any]],
    first_site_name: str,
    first_subject_key: str,
    first_interval_name: str,
) -> dict[str, Any]:
    scenario = request.param
    if scenario == "register":
        return typed_record(site_name=first_site_name)
    if scenario == "scheduled":
        return typed_record(subject_key=first_subject_key, interval_name=first_interval_name)
    if scenario == "new":
        return typed_record(subject_key=first_subject_key)
    raise ValueError(f"Unknown record scenario: {scenario}")
