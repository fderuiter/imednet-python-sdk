import os

import pytest
from imednet.async_sdk import AsyncImednetSDK
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


def _create_sdk() -> ImednetSDK:
    return ImednetSDK(api_key=API_KEY, security_key=SECURITY_KEY, base_url=BASE_URL)


def test_list_studies() -> None:
    with _create_sdk() as sdk:
        studies = sdk.studies.list()
        assert isinstance(studies, list)
        if studies:
            assert hasattr(studies[0], "study_key")


def test_list_sites() -> None:
    with _create_sdk() as sdk:
        studies = sdk.studies.list()
        if not studies:
            pytest.skip("No studies available to test sites endpoint")
        study_key = studies[0].study_key
        sites = sdk.sites.list(study_key=study_key)
        assert isinstance(sites, list)


@pytest.mark.asyncio
async def test_async_studies() -> None:
    async with AsyncImednetSDK(
        api_key=API_KEY,
        security_key=SECURITY_KEY,
        base_url=BASE_URL,
    ) as sdk:
        studies = await sdk.studies.async_list()
        assert isinstance(studies, list)
