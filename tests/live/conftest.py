import asyncio
import os
from typing import AsyncIterator, Generator, Iterator

import pytest

from imednet.sdk import AsyncImednetSDK, ImednetSDK
from tests.live.helpers import get_form_key, get_study_key

API_KEY = os.getenv("IMEDNET_API_KEY")
SECURITY_KEY = os.getenv("IMEDNET_SECURITY_KEY")
BASE_URL = os.getenv("IMEDNET_BASE_URL")
RUN_E2E = os.getenv("IMEDNET_RUN_E2E") == "1"


@pytest.fixture(scope="session", autouse=True)
def _check_live_env() -> None:
    if not RUN_E2E or not (API_KEY and SECURITY_KEY):
        pytest.skip(
            "Set IMEDNET_RUN_E2E=1 and provide IMEDNET_API_KEY/IMEDNET_SECURITY_KEY "
            "to run live tests"
        )


@pytest.fixture(scope="session")
def sdk() -> Iterator[ImednetSDK]:
    with ImednetSDK(api_key=API_KEY, security_key=SECURITY_KEY, base_url=BASE_URL) as client:
        yield client


@pytest.fixture(scope="session")
async def async_sdk(event_loop: asyncio.AbstractEventLoop) -> AsyncIterator[AsyncImednetSDK]:
    client = AsyncImednetSDK(api_key=API_KEY, security_key=SECURITY_KEY, base_url=BASE_URL)
    try:
        yield client
    finally:
        await client.aclose()


@pytest.fixture(scope="session")
def study_key(sdk: ImednetSDK) -> str:
    return get_study_key(sdk)


@pytest.fixture(scope="session")
def first_form_key(sdk: ImednetSDK, study_key: str) -> str:
    return get_form_key(sdk, study_key)


@pytest.fixture(scope="session")
def generated_batch_id(sdk: ImednetSDK, study_key: str, first_form_key: str) -> str:
    record = {"formKey": first_form_key, "data": {}}
    job = sdk.records.create(study_key, [record])
    return job.batch_id


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create an asyncio event loop for session-scoped async fixtures."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()
