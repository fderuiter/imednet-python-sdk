import os
from typing import AsyncIterator, Iterator

import pytest
import pytest_asyncio
from imednet.async_sdk import AsyncImednetSDK
from imednet.core.exceptions import ServerError
from imednet.models.forms import Form
from imednet.models.intervals import Interval
from imednet.models.queries import Query
from imednet.models.record_revisions import RecordRevision
from imednet.models.records import Record
from imednet.models.sites import Site
from imednet.models.studies import Study
from imednet.models.subjects import Subject
from imednet.models.users import User
from imednet.models.variables import Variable
from imednet.models.visits import Visit
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
    client = AsyncImednetSDK(
        api_key=API_KEY,
        security_key=SECURITY_KEY,
        base_url=BASE_URL,
    )
    try:
        yield client
    finally:
        await client.aclose()


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
    if sites:
        assert isinstance(sites[0], Site)


def test_get_study(sdk: ImednetSDK, study_key: str) -> None:
    try:
        study = sdk.studies.get(study_key)
    except ServerError as exc:
        pytest.fail(f"Server error retrieving study {study_key}: {exc.response}")
    else:
        assert study.study_key == study_key


def test_list_forms(sdk: ImednetSDK, study_key: str) -> None:
    forms = sdk.forms.list(study_key=study_key)
    assert isinstance(forms, list)
    if forms:
        assert isinstance(forms[0], Form)


def test_list_subjects(sdk: ImednetSDK, study_key: str) -> None:
    subjects = sdk.subjects.list(study_key=study_key)
    assert isinstance(subjects, list)
    if subjects:
        assert isinstance(subjects[0], Subject)


def test_list_records(sdk: ImednetSDK, study_key: str) -> None:
    records = sdk.records.list(study_key=study_key)
    assert isinstance(records, list)
    if records:
        assert isinstance(records[0], Record)


def test_list_intervals(sdk: ImednetSDK, study_key: str) -> None:
    intervals = sdk.intervals.list(study_key=study_key)
    assert isinstance(intervals, list)
    if intervals:
        assert isinstance(intervals[0], Interval)


def test_list_visits(sdk: ImednetSDK, study_key: str) -> None:
    visits = sdk.visits.list(study_key=study_key)
    assert isinstance(visits, list)
    if visits:
        assert isinstance(visits[0], Visit)


def test_list_variables(sdk: ImednetSDK, study_key: str) -> None:
    variables = sdk.variables.list(study_key=study_key)
    assert isinstance(variables, list)
    if variables:
        assert isinstance(variables[0], Variable)


def test_list_users(sdk: ImednetSDK, study_key: str) -> None:
    users = sdk.users.list(study_key=study_key)
    assert isinstance(users, list)
    if users:
        assert isinstance(users[0], User)


def test_list_queries(sdk: ImednetSDK, study_key: str) -> None:
    queries = sdk.queries.list(study_key=study_key)
    assert isinstance(queries, list)
    if queries:
        assert isinstance(queries[0], Query)


def test_list_record_revisions(sdk: ImednetSDK, study_key: str) -> None:
    revisions = sdk.record_revisions.list(study_key=study_key)
    assert isinstance(revisions, list)
    if revisions:
        assert isinstance(revisions[0], RecordRevision)


@pytest.mark.asyncio(scope="module")
async def test_async_studies(async_sdk: AsyncImednetSDK) -> None:
    studies = await async_sdk.studies.async_list()
    assert isinstance(studies, list)
    assert studies, "No studies returned from server"
    assert isinstance(studies[0], Study)
