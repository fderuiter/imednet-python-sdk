import os
from typing import AsyncIterator, Iterator

import pytest
import pytest_asyncio
from imednet.async_sdk import AsyncImednetSDK
from imednet.core.exceptions import ServerError
from imednet.models.studies import Study
from imednet.sdk import ImednetSDK

API_KEY = os.getenv("IMEDNET_API_KEY")
SECURITY_KEY = os.getenv("IMEDNET_SECURITY_KEY")
BASE_URL = os.getenv("IMEDNET_BASE_URL")
RUN_E2E = os.getenv("IMEDNET_RUN_E2E") == "1"

pytestmark = pytest.mark.skipif(
    not RUN_E2E or not (API_KEY and SECURITY_KEY),
    reason=(
        "Set IMEDNET_RUN_E2E=1 and provide IMEDNET_API_KEY/IMEDNET_SECURITY_KEY" " to run e2e tests"
    ),
)


@pytest.fixture(scope="module")
def sdk() -> Iterator[ImednetSDK]:
    with ImednetSDK(api_key=API_KEY, security_key=SECURITY_KEY, base_url=BASE_URL) as client:
        yield client


@pytest_asyncio.fixture(scope="module")
async def async_sdk() -> AsyncIterator[AsyncImednetSDK]:
    async with AsyncImednetSDK(
        api_key=API_KEY,
        security_key=SECURITY_KEY,
        base_url=BASE_URL,
    ) as client:
        yield client


@pytest.fixture(scope="module")
def study_key(sdk: ImednetSDK) -> str:
    studies = sdk.studies.list()
    if not studies:
        pytest.skip("No studies available for e2e tests")
    return studies[0].study_key


def test_list_studies(sdk: ImednetSDK) -> None:
    studies = sdk.studies.list()
    assert isinstance(studies, list)
    assert studies, "No studies returned from server"
    assert isinstance(studies[0], Study)


def test_list_sites(sdk: ImednetSDK, study_key: str) -> None:
    sites = sdk.sites.list(study_key=study_key)
    assert isinstance(sites, list)


def test_get_study(sdk: ImednetSDK, study_key: str) -> None:
    try:
        study = sdk.studies.get(study_key)
    except ServerError as exc:
        pytest.skip(f"Server error retrieving study: {exc}")
    else:
        assert study.study_key == study_key


def test_list_forms(sdk: ImednetSDK, study_key: str) -> None:
    forms = sdk.forms.list(study_key=study_key)
    assert isinstance(forms, list)


def test_list_subjects(sdk: ImednetSDK, study_key: str) -> None:
    subjects = sdk.subjects.list(study_key=study_key)
    assert isinstance(subjects, list)


def test_list_records(sdk: ImednetSDK, study_key: str) -> None:
    records = sdk.records.list(study_key=study_key)
    assert isinstance(records, list)


@pytest.mark.asyncio
async def test_async_studies(async_sdk: AsyncImednetSDK) -> None:
    studies = await async_sdk.studies.async_list()
    assert isinstance(studies, list)
    assert studies, "No studies returned from server"
