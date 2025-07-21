import os
from typing import AsyncIterator, Iterator

import pytest

from imednet.sdk import AsyncImednetSDK, ImednetSDK

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
async def async_sdk() -> AsyncIterator[AsyncImednetSDK]:
    client = AsyncImednetSDK(api_key=API_KEY, security_key=SECURITY_KEY, base_url=BASE_URL)
    try:
        yield client
    finally:
        await client.aclose()


@pytest.fixture(scope="session")
def study_key(sdk: ImednetSDK) -> str:
    studies = sdk.studies.list()
    if not studies:
        pytest.skip("No studies available for live tests")
    return studies[0].study_key


@pytest.fixture(scope="session")
def first_form_key(sdk: ImednetSDK, study_key: str) -> str:
    override = os.getenv("IMEDNET_FORM_KEY")
    if override:
        return override
    forms = sdk.forms.list(study_key=study_key)
    if not forms:
        pytest.skip("No forms available for record creation")
    return forms[0].form_key


@pytest.fixture(scope="session")
def generated_batch_id(sdk: ImednetSDK, study_key: str, first_form_key: str) -> str:
    record = {"formKey": first_form_key, "data": {}}
    job = sdk.records.create(study_key, [record])
    return job.batch_id
