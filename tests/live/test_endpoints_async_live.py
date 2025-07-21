import os
from typing import AsyncIterator, Iterator

import pytest
import pytest_asyncio

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
        pytest.skip("No studies available for live tests")
    return studies[0].study_key


@pytest.mark.asyncio(scope="module")
async def test_async_sites(async_sdk: AsyncImednetSDK, study_key: str) -> None:
    sites = await async_sdk.sites.async_list(study_key)
    assert isinstance(sites, list)
    if sites:
        site = await async_sdk.sites.async_get(study_key, sites[0].site_id)
        assert site.site_id == sites[0].site_id


@pytest.mark.asyncio(scope="module")
async def test_async_subjects(async_sdk: AsyncImednetSDK, study_key: str) -> None:
    subjects = await async_sdk.subjects.async_list(study_key)
    assert isinstance(subjects, list)
    if subjects:
        subject = await async_sdk.subjects.async_get(study_key, subjects[0].subject_key)
        assert subject.subject_key == subjects[0].subject_key


@pytest.mark.asyncio(scope="module")
async def test_async_records(async_sdk: AsyncImednetSDK, study_key: str) -> None:
    records = await async_sdk.records.async_list(study_key)
    assert isinstance(records, list)
    if records:
        record = await async_sdk.records.async_get(study_key, records[0].record_id)
        assert record.record_id == records[0].record_id


@pytest.mark.asyncio(scope="module")
async def test_async_intervals(async_sdk: AsyncImednetSDK, study_key: str) -> None:
    intervals = await async_sdk.intervals.async_list(study_key)
    assert isinstance(intervals, list)
    if intervals:
        interval = await async_sdk.intervals.async_get(study_key, intervals[0].interval_id)
        assert interval.interval_id == intervals[0].interval_id


@pytest.mark.asyncio(scope="module")
async def test_async_visits(async_sdk: AsyncImednetSDK, study_key: str) -> None:
    visits = await async_sdk.visits.async_list(study_key)
    assert isinstance(visits, list)
    if visits:
        visit = await async_sdk.visits.async_get(study_key, visits[0].visit_id)
        assert visit.visit_id == visits[0].visit_id


@pytest.mark.asyncio(scope="module")
async def test_async_variables(async_sdk: AsyncImednetSDK, study_key: str) -> None:
    variables = await async_sdk.variables.async_list(study_key)
    assert isinstance(variables, list)
    if variables:
        variable = await async_sdk.variables.async_get(study_key, variables[0].variable_id)
        assert variable.variable_id == variables[0].variable_id


@pytest.mark.asyncio(scope="module")
async def test_async_forms(async_sdk: AsyncImednetSDK, study_key: str) -> None:
    forms = await async_sdk.forms.async_list(study_key)
    assert isinstance(forms, list)
    if forms:
        form = await async_sdk.forms.async_get(study_key, forms[0].form_id)
        assert form.form_id == forms[0].form_id


@pytest.mark.asyncio(scope="module")
async def test_async_queries(async_sdk: AsyncImednetSDK, study_key: str) -> None:
    queries = await async_sdk.queries.async_list(study_key)
    assert isinstance(queries, list)
    if queries:
        query = await async_sdk.queries.async_get(study_key, queries[0].annotation_id)
        assert query.annotation_id == queries[0].annotation_id


@pytest.mark.asyncio(scope="module")
async def test_async_record_revisions(async_sdk: AsyncImednetSDK, study_key: str) -> None:
    revisions = await async_sdk.record_revisions.async_list(study_key)
    assert isinstance(revisions, list)
    if revisions:
        rev = await async_sdk.record_revisions.async_get(study_key, revisions[0].record_revision_id)
        assert rev.record_revision_id == revisions[0].record_revision_id


@pytest.mark.asyncio(scope="module")
async def test_async_users(async_sdk: AsyncImednetSDK, study_key: str) -> None:
    users = await async_sdk.users.async_list(study_key)
    assert isinstance(users, list)
    if users:
        user = await async_sdk.users.async_get(study_key, users[0].user_id)
        assert user.user_id == users[0].user_id


@pytest.mark.asyncio(scope="module")
async def test_async_codings(async_sdk: AsyncImednetSDK, study_key: str) -> None:
    codings = await async_sdk.codings.async_list(study_key)
    assert isinstance(codings, list)
    if codings:
        coding = await async_sdk.codings.async_get(study_key, str(codings[0].coding_id))
        assert coding.coding_id == codings[0].coding_id


@pytest.mark.asyncio(scope="module")
async def test_async_create_and_poll(
    async_sdk: AsyncImednetSDK,
    study_key: str,
    first_form_key: str,
) -> None:
    record = {"formKey": first_form_key, "data": {}}
    job = await async_sdk.records.async_create(study_key, [record])
    polled = await async_sdk.jobs.async_get(study_key, job.batch_id)
    assert polled.batch_id == job.batch_id
