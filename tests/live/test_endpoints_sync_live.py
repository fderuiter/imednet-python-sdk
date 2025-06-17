import os
from typing import Iterator

import pytest
from imednet import ImednetSDK
from imednet.core.exceptions import ServerError
from imednet.models.codings import Coding
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
    studies = sdk.studies.list()
    if not studies:
        pytest.skip("No studies available for live tests")
    return studies[0].study_key


def test_list_studies(sdk: ImednetSDK) -> None:
    studies = sdk.studies.list()
    assert isinstance(studies, list)
    assert studies, "No studies returned from server"
    assert isinstance(studies[0], Study)
    study = sdk.studies.get(studies[0].study_key)
    assert study.study_key == studies[0].study_key


def test_list_sites(sdk: ImednetSDK, study_key: str) -> None:
    sites = sdk.sites.list(study_key=study_key)
    assert isinstance(sites, list)
    if sites:
        assert isinstance(sites[0], Site)
        site = sdk.sites.get(study_key, sites[0].site_id)
        assert site.site_id == sites[0].site_id


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
        form = sdk.forms.get(study_key, forms[0].form_id)
        assert form.form_id == forms[0].form_id


def test_list_subjects(sdk: ImednetSDK, study_key: str) -> None:
    subjects = sdk.subjects.list(study_key=study_key)
    assert isinstance(subjects, list)
    if subjects:
        assert isinstance(subjects[0], Subject)
        subject = sdk.subjects.get(study_key, subjects[0].subject_key)
        assert subject.subject_key == subjects[0].subject_key


def test_list_records(sdk: ImednetSDK, study_key: str) -> None:
    records = sdk.records.list(study_key=study_key)
    assert isinstance(records, list)
    if records:
        assert isinstance(records[0], Record)
        record = sdk.records.get(study_key, records[0].record_id)
        assert record.record_id == records[0].record_id


def test_list_intervals(sdk: ImednetSDK, study_key: str) -> None:
    intervals = sdk.intervals.list(study_key=study_key)
    assert isinstance(intervals, list)
    if intervals:
        assert isinstance(intervals[0], Interval)
        interval = sdk.intervals.get(study_key, intervals[0].interval_id)
        assert interval.interval_id == intervals[0].interval_id


def test_list_visits(sdk: ImednetSDK, study_key: str) -> None:
    visits = sdk.visits.list(study_key=study_key)
    assert isinstance(visits, list)
    if visits:
        assert isinstance(visits[0], Visit)
        visit = sdk.visits.get(study_key, visits[0].visit_id)
        assert visit.visit_id == visits[0].visit_id


def test_list_variables(sdk: ImednetSDK, study_key: str) -> None:
    variables = sdk.variables.list(study_key=study_key)
    assert isinstance(variables, list)
    if variables:
        assert isinstance(variables[0], Variable)
        variable = sdk.variables.get(study_key, variables[0].variable_id)
        assert variable.variable_id == variables[0].variable_id


def test_list_users(sdk: ImednetSDK, study_key: str) -> None:
    users = sdk.users.list(study_key=study_key)
    assert isinstance(users, list)
    if users:
        assert isinstance(users[0], User)
        user = sdk.users.get(study_key, users[0].user_id)
        assert user.user_id == users[0].user_id


def test_list_queries(sdk: ImednetSDK, study_key: str) -> None:
    queries = sdk.queries.list(study_key=study_key)
    assert isinstance(queries, list)
    if queries:
        assert isinstance(queries[0], Query)
        query = sdk.queries.get(study_key, queries[0].annotation_id)
        assert query.annotation_id == queries[0].annotation_id


def test_list_record_revisions(sdk: ImednetSDK, study_key: str) -> None:
    revisions = sdk.record_revisions.list(study_key=study_key)
    assert isinstance(revisions, list)
    if revisions:
        assert isinstance(revisions[0], RecordRevision)
        revision = sdk.record_revisions.get(study_key, revisions[0].record_revision_id)
        assert revision.record_revision_id == revisions[0].record_revision_id


def test_job_get_known_batch(sdk: ImednetSDK, study_key: str) -> None:
    batch_id = os.getenv("IMEDNET_BATCH_ID")
    if not batch_id:
        pytest.skip("IMEDNET_BATCH_ID not set")
    job = sdk.jobs.get(study_key, batch_id)
    assert job.batch_id == batch_id


def test_create_record_and_poll_job(sdk: ImednetSDK, study_key: str) -> None:
    form_key = os.getenv("IMEDNET_FORM_KEY")
    if not form_key:
        pytest.skip("IMEDNET_FORM_KEY not set for record creation")
    record = {"formKey": form_key, "data": {}}
    job = sdk.records.create(study_key, [record])
    assert job.batch_id
    polled = sdk.jobs.get(study_key, job.batch_id)
    assert polled.batch_id == job.batch_id


def test_list_codings(sdk: ImednetSDK, study_key: str) -> None:
    codings = sdk.codings.list(study_key=study_key)
    assert isinstance(codings, list)
    if codings:
        assert isinstance(codings[0], Coding)
        coding = sdk.codings.get(study_key, str(codings[0].coding_id))
        assert coding.coding_id == codings[0].coding_id
