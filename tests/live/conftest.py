"""Unit tests for conftest."""

import asyncio
import logging
import os
from collections.abc import AsyncIterator, Callable, Generator, Iterator
from typing import Any

import pytest

from imednet.discovery import (
    NoLiveDataError,
    discover_interval_name,
    discover_site_name,
    discover_subject_key,
)
from imednet.sdk import AsyncImednetSDK, ImednetSDK
from imednet.testing import typed_values
from tests.live.helpers import get_form_key, get_study_key, require_mutation

pytestmark = pytest.mark.live

RUN_E2E = os.getenv("IMEDNET_RUN_E2E") == "1"
ALLOW_MUTATION = os.getenv("IMEDNET_ALLOW_MUTATION") == "1"
STUDY_KEY_OVERRIDE = os.getenv("IMEDNET_STUDY_KEY")
BATCH_ID_OVERRIDE = os.getenv("IMEDNET_BATCH_ID")

logger = logging.getLogger(__name__)


def _typed_value(var_type: str) -> Any:
    """Return a deterministic example value for ``var_type``."""
    return typed_values.value_for(var_type) or ""


def _print_startup_context() -> None:
    """Print environment context so operators can verify the correct target."""
    print("\n[live-tests] ── startup context ──────────────────────────")
    print(f"[live-tests]   IMEDNET_RUN_E2E       : {os.getenv('IMEDNET_RUN_E2E', '(not set)')}")
    print(
        f"[live-tests]   IMEDNET_ALLOW_MUTATION: {os.getenv('IMEDNET_ALLOW_MUTATION', '(not set)')}"
    )
    if STUDY_KEY_OVERRIDE:
        print(f"[live-tests]   IMEDNET_STUDY_KEY     : {STUDY_KEY_OVERRIDE} (pinned)")
    else:
        print("[live-tests]   IMEDNET_STUDY_KEY     : (auto-discover)")
    print(f"[live-tests]   IMEDNET_BASE_URL      : {os.getenv('IMEDNET_BASE_URL') or '(default)'}")
    print("[live-tests] ───────────────────────────────────────────────\n")


@pytest.fixture(scope="session", autouse=True)
def _check_live_env() -> None:
    """Helper function to  check live env."""
    _print_startup_context()
    if not RUN_E2E:
        pytest.skip("Set IMEDNET_RUN_E2E=1 to run live tests")

    from imednet.config import load_config

    load_config()
    logger.info("Live test environment configured (mutation=%s)", ALLOW_MUTATION)


@pytest.fixture(scope="session")
def allow_mutation() -> bool:
    """Return ``True`` when ``IMEDNET_ALLOW_MUTATION=1`` is set."""
    return ALLOW_MUTATION


@pytest.fixture(scope="session")
def sdk() -> Iterator[ImednetSDK]:
    """Helper function to sdk."""
    from imednet.config import load_config

    config = load_config()
    with ImednetSDK(
        api_key=config.api_key, security_key=config.security_key, base_url=config.base_url
    ) as client:
        yield client


@pytest.fixture(scope="session")
async def async_sdk(event_loop: asyncio.AbstractEventLoop) -> AsyncIterator[AsyncImednetSDK]:
    """Provides a session-scoped asynchronous ImednetSDK client.

    The `event_loop` parameter is required to ensure proper async fixture teardown and SDK cleanup,
    as pytest needs an explicit event loop for session-scoped async fixtures.
    """
    from imednet.config import load_config

    config = load_config()
    client = AsyncImednetSDK(
        api_key=config.api_key, security_key=config.security_key, base_url=config.base_url
    )
    try:
        yield client
    finally:
        await client.aclose()


@pytest.fixture(scope="session")
def study_key(sdk: ImednetSDK) -> str:
    """Helper function to study key."""
    return get_study_key(sdk)


@pytest.fixture(scope="session")
def first_form_key(sdk: ImednetSDK, study_key: str) -> str:
    """Helper function to first form key."""
    return get_form_key(sdk, study_key)


@pytest.fixture(scope="session")
def first_site_name(sdk: ImednetSDK, study_key: str) -> str:
    """Helper function to first site name."""
    try:
        return discover_site_name(sdk, study_key)
    except NoLiveDataError as exc:
        pytest.skip(str(exc))


@pytest.fixture(scope="session")
def first_subject_key(sdk: ImednetSDK, study_key: str) -> str:
    """Helper function to first subject key."""
    try:
        return discover_subject_key(sdk, study_key)
    except NoLiveDataError as exc:
        pytest.skip(str(exc))


@pytest.fixture(scope="session")
def first_interval_name(sdk: ImednetSDK, study_key: str) -> str:
    """Helper function to first interval name."""
    try:
        return discover_interval_name(sdk, study_key)
    except NoLiveDataError as exc:
        pytest.skip(str(exc))


@pytest.fixture(scope="session")
def generated_batch_id(sdk: ImednetSDK, study_key: str, first_form_key: str) -> str:
    """Return a batch ID for job-polling tests.

    Uses ``IMEDNET_BATCH_ID`` when set (read-only path).  Otherwise requires
    ``IMEDNET_ALLOW_MUTATION=1`` and creates a record to obtain a fresh batch ID.
    """
    if BATCH_ID_OVERRIDE:
        return BATCH_ID_OVERRIDE

    require_mutation()

    variables = list(sdk.variables.list(study_key=study_key, formKey=first_form_key))
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
    if not job.batch_id:
        pytest.skip("Job completed synchronously without a batch ID")
    return job.batch_id


@pytest.fixture(scope="session")
def typed_record(
    sdk: ImednetSDK,
    study_key: str,
    first_form_key: str,
) -> Callable[..., dict[str, Any]]:
    """Helper function to typed record."""
    variables = list(sdk.variables.list(study_key=study_key, formKey=first_form_key))
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
        """Helper function to build."""
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
    """Helper function to record payload."""
    scenario = request.param
    if scenario == "register":
        return typed_record(site_name=first_site_name)
    if scenario == "scheduled":
        return typed_record(subject_key=first_subject_key, interval_name=first_interval_name)
    if scenario == "new":
        return typed_record(subject_key=first_subject_key)
    raise ValueError(f"Unknown record scenario: {scenario}")


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create an asyncio event loop for session-scoped async fixtures."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()
