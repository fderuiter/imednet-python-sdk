import os
from typing import Iterator

import pytest
from imednet.sdk import ImednetSDK

API_KEY = os.getenv("IMEDNET_API_KEY")
SECURITY_KEY = os.getenv("IMEDNET_SECURITY_KEY")
BASE_URL = os.getenv("IMEDNET_BASE_URL")
RUN_E2E = os.getenv("IMEDNET_RUN_E2E") == "1"

pytestmark = pytest.mark.skipif(
    not RUN_E2E or not (API_KEY and SECURITY_KEY),
    reason=(
        "Set IMEDNET_RUN_E2E=1 and provide IMEDNET_API_KEY/IMEDNET_SECURITY_KEY to run e2e tests"
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
        pytest.skip("No studies available for e2e tests")
    return studies[0].study_key


def test_get_studies(sdk: ImednetSDK) -> None:
    assert sdk.get_studies()


def test_get_records(sdk: ImednetSDK, study_key: str) -> None:
    records = sdk.get_records(study_key)
    assert isinstance(records, list)


def test_get_sites(sdk: ImednetSDK, study_key: str) -> None:
    sites = sdk.get_sites(study_key)
    assert isinstance(sites, list)


def test_get_subjects(sdk: ImednetSDK, study_key: str) -> None:
    subjects = sdk.get_subjects(study_key)
    assert isinstance(subjects, list)


def test_get_forms(sdk: ImednetSDK, study_key: str) -> None:
    forms = sdk.get_forms(study_key)
    assert isinstance(forms, list)


def test_get_intervals(sdk: ImednetSDK, study_key: str) -> None:
    intervals = sdk.get_intervals(study_key)
    assert isinstance(intervals, list)


def test_get_variables(sdk: ImednetSDK, study_key: str) -> None:
    vars_ = sdk.get_variables(study_key)
    assert isinstance(vars_, list)


def test_get_visits(sdk: ImednetSDK, study_key: str) -> None:
    visits = sdk.get_visits(study_key)
    assert isinstance(visits, list)


def test_get_codings(sdk: ImednetSDK, study_key: str) -> None:
    codings = sdk.get_codings(study_key)
    assert isinstance(codings, list)


def test_get_queries(sdk: ImednetSDK, study_key: str) -> None:
    queries = sdk.get_queries(study_key)
    assert isinstance(queries, list)


def test_get_record_revisions(sdk: ImednetSDK, study_key: str) -> None:
    revs = sdk.get_record_revisions(study_key)
    assert isinstance(revs, list)


def test_get_users(sdk: ImednetSDK, study_key: str) -> None:
    users = sdk.get_users(study_key)
    assert isinstance(users, list)


def test_get_job(sdk: ImednetSDK, study_key: str) -> None:
    batch_id = os.getenv("IMEDNET_BATCH_ID")
    if not batch_id:
        pytest.skip("IMEDNET_BATCH_ID not set")
    job = sdk.get_job(study_key, batch_id)
    assert job.batch_id == batch_id


def test_poll_job(sdk: ImednetSDK, study_key: str) -> None:
    batch_id = os.getenv("IMEDNET_BATCH_ID")
    if not batch_id:
        pytest.skip("IMEDNET_BATCH_ID not set")
    job = sdk.poll_job(study_key, batch_id, interval=1, timeout=5)
    assert job.batch_id == batch_id
