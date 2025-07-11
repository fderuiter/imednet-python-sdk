import os
from typing import Iterator

import pytest

from imednet.models.records import RegisterSubjectRequest
from imednet.sdk import ImednetSDK
from imednet.workflows import (
    RegisterSubjectsWorkflow,
    async_get_study_structure,
    get_study_structure,
)

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


@pytest.fixture(scope="module")
def study_key(sdk: ImednetSDK) -> str:
    studies = sdk.get_studies()
    if not studies:
        pytest.skip("No studies available for live tests")
    return studies[0].study_key


@pytest.fixture(scope="module")
def first_subject_key(sdk: ImednetSDK, study_key: str) -> str:
    subs = sdk.get_subjects(study_key)
    if not subs:
        pytest.skip("No subjects available for workflow tests")
    return subs[0].subject_key


def test_get_study_structure(sdk: ImednetSDK, study_key: str) -> None:
    structure = get_study_structure(sdk, study_key)
    assert structure.study_key == study_key


@pytest.mark.asyncio(scope="module")
async def test_async_get_study_structure(study_key: str) -> None:
    async with ImednetSDK(
        api_key=API_KEY,
        security_key=SECURITY_KEY,
        base_url=BASE_URL,
        enable_async=True,
    ) as sdk_async:
        struct = await async_get_study_structure(sdk_async, study_key)
        assert struct.study_key == study_key


def test_register_subjects_workflow(sdk: ImednetSDK, study_key: str) -> None:
    if os.getenv("IMEDNET_ALLOW_MUTATION") != "1":
        pytest.skip("Mutating tests are disabled")
    forms = sdk.get_forms(study_key)
    sites = sdk.get_sites(study_key)
    if not forms or not sites:
        pytest.skip("No forms/sites for subject registration")
    req = RegisterSubjectRequest(form_key=forms[0].form_key, site_name=sites[0].site_name, data={})
    wf = RegisterSubjectsWorkflow(sdk)
    job = wf.register_subjects(study_key, [req])
    assert job.batch_id


def test_extract_records_by_criteria(sdk: ImednetSDK, study_key: str) -> None:
    wf = sdk.workflows.data_extraction
    records = wf.extract_records_by_criteria(study_key)
    assert isinstance(records, list)


def test_extract_audit_trail(sdk: ImednetSDK, study_key: str) -> None:
    wf = sdk.workflows.data_extraction
    trail = wf.extract_audit_trail(study_key)
    assert isinstance(trail, list)


def test_subject_data_workflow(sdk: ImednetSDK, study_key: str, first_subject_key: str) -> None:
    data = sdk.workflows.subject_data.get_all_subject_data(study_key, first_subject_key)
    assert data.subject_details is not None


def test_query_management_open_queries(sdk: ImednetSDK, study_key: str) -> None:
    wf = sdk.workflows.query_management
    assert isinstance(wf.get_open_queries(study_key), list)


def test_query_management_for_subject(
    sdk: ImednetSDK, study_key: str, first_subject_key: str
) -> None:
    wf = sdk.workflows.query_management
    queries = wf.get_queries_for_subject(study_key, first_subject_key)
    assert isinstance(queries, list)


def test_query_management_by_site(sdk: ImednetSDK, study_key: str) -> None:
    wf = sdk.workflows.query_management
    sites = sdk.get_sites(study_key)
    if not sites:
        pytest.skip("No sites available")
    assert isinstance(wf.get_queries_by_site(study_key, sites[0].site_name), list)


def test_query_management_state_counts(sdk: ImednetSDK, study_key: str) -> None:
    wf = sdk.workflows.query_management
    counts = wf.get_query_state_counts(study_key)
    assert isinstance(counts, dict)


def test_record_mapper_dataframe(sdk: ImednetSDK, study_key: str) -> None:
    df = sdk.workflows.record_mapper.dataframe(study_key)
    assert hasattr(df, "columns")


def test_record_update_submit_batch(sdk: ImednetSDK, study_key: str) -> None:
    if os.getenv("IMEDNET_ALLOW_MUTATION") != "1":
        pytest.skip("Mutating tests are disabled")
    job = sdk.workflows.record_update.create_or_update_records(study_key, [])
    assert job.batch_id


def test_record_update_register_subject(sdk: ImednetSDK, study_key: str) -> None:
    if os.getenv("IMEDNET_ALLOW_MUTATION") != "1":
        pytest.skip("Mutating tests are disabled")
    job = sdk.workflows.record_update.register_subject(
        study_key,
        "FORM",
        "SITE",
        {},
        wait_for_completion=False,
    )
    assert job.batch_id


def test_record_update_update_scheduled(
    sdk: ImednetSDK, study_key: str, first_subject_key: str
) -> None:
    if os.getenv("IMEDNET_ALLOW_MUTATION") != "1":
        pytest.skip("Mutating tests are disabled")
    job = sdk.workflows.record_update.update_scheduled_record(
        study_key,
        "FORM",
        first_subject_key,
        "INTERVAL",
        {},
        wait_for_completion=False,
    )
    assert job.batch_id


def test_record_update_create_new(sdk: ImednetSDK, study_key: str, first_subject_key: str) -> None:
    if os.getenv("IMEDNET_ALLOW_MUTATION") != "1":
        pytest.skip("Mutating tests are disabled")
    job = sdk.workflows.record_update.create_new_record(
        study_key,
        "FORM",
        first_subject_key,
        {},
        wait_for_completion=False,
    )
    assert job.batch_id
