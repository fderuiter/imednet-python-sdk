from unittest.mock import AsyncMock

import pytest

import imednet.api.endpoints.codings as codings
import imednet.api.endpoints.forms as forms
import imednet.api.endpoints.intervals as intervals
import imednet.api.endpoints.jobs as jobs
import imednet.api.endpoints.queries as queries
import imednet.api.endpoints.record_revisions as record_revisions
import imednet.api.endpoints.records as records
import imednet.api.endpoints.sites as sites
import imednet.api.endpoints.subjects as subjects
import imednet.api.endpoints.users as users
import imednet.api.endpoints.variables as variables
import imednet.api.endpoints.visits as visits
from imednet.api.models.codings import Coding
from imednet.api.models.forms import Form
from imednet.api.models.intervals import Interval
from imednet.api.models.jobs import JobStatus
from imednet.api.models.queries import Query
from imednet.api.models.record_revisions import RecordRevision
from imednet.api.models.records import Record
from imednet.api.models.sites import Site
from imednet.api.models.subjects import Subject
from imednet.api.models.users import User
from imednet.api.models.variables import Variable
from imednet.api.models.visits import Visit


@pytest.mark.asyncio
async def test_async_list_records(
    async_dummy_client, context, async_paginator_factory, patch_build_filter
):
    ep = records.RecordsEndpoint(async_dummy_client, context, async_client=async_dummy_client)
    captured = async_paginator_factory([{"recordId": 1}])
    filter_capture = patch_build_filter(records)
    result = await ep.async_list(study_key="S1", record_data_filter="x")
    assert captured["path"] == "/api/v1/edc/studies/S1/records"
    assert captured["params"] == {"filter": "FILTERED", "recordDataFilter": "x"}
    assert filter_capture["filters"] == {"studyKey": "S1"}
    assert isinstance(result[0], Record)


@pytest.mark.asyncio
async def test_async_list_codings(async_dummy_client, context, async_paginator_factory):
    ep = codings.CodingsEndpoint(async_dummy_client, context, async_client=async_dummy_client)
    captured = async_paginator_factory([{"codingId": 1}])
    result = await ep.async_list(study_key="S1")
    assert captured["path"] == "/api/v1/edc/studies/S1/codings"
    assert isinstance(result[0], Coding)


@pytest.mark.asyncio
async def test_async_list_forms(async_dummy_client, context, async_paginator_factory):
    context.set_default_study_key("S1")
    ep = forms.FormsEndpoint(async_dummy_client, context, async_client=async_dummy_client)
    captured = async_paginator_factory([{"formId": 1}])
    result = await ep.async_list()
    assert captured["path"] == "/api/v1/edc/studies/S1/forms"
    assert isinstance(result[0], Form)


@pytest.mark.asyncio
async def test_async_list_intervals(async_dummy_client, context, async_paginator_factory):
    context.set_default_study_key("S1")
    ep = intervals.IntervalsEndpoint(async_dummy_client, context, async_client=async_dummy_client)
    captured = async_paginator_factory([{"intervalId": 1}])
    result = await ep.async_list()
    assert captured["path"] == "/api/v1/edc/studies/S1/intervals"
    assert isinstance(result[0], Interval)


@pytest.mark.asyncio
async def test_async_list_queries(async_dummy_client, context, async_paginator_factory):
    context.set_default_study_key("S1")
    ep = queries.QueriesEndpoint(async_dummy_client, context, async_client=async_dummy_client)
    captured = async_paginator_factory([{"annotationId": 1}])
    result = await ep.async_list(status="new")
    assert captured["path"] == "/api/v1/edc/studies/S1/queries"
    assert isinstance(result[0], Query)


@pytest.mark.asyncio
async def test_async_list_record_revisions(async_dummy_client, context, async_paginator_factory):
    context.set_default_study_key("S1")
    ep = record_revisions.RecordRevisionsEndpoint(
        async_dummy_client,
        context,
        async_client=async_dummy_client,
    )
    captured = async_paginator_factory([{"recordRevisionId": 1}])
    result = await ep.async_list(status="x")
    assert captured["path"] == "/api/v1/edc/studies/S1/recordRevisions"
    assert isinstance(result[0], RecordRevision)


@pytest.mark.asyncio
async def test_async_list_sites(async_dummy_client, context, async_paginator_factory):
    ep = sites.SitesEndpoint(async_dummy_client, context, async_client=async_dummy_client)
    captured = async_paginator_factory([{"siteId": 1}])
    result = await ep.async_list(study_key="S1")
    assert captured["path"] == "/api/v1/edc/studies/S1/sites"
    assert isinstance(result[0], Site)


@pytest.mark.asyncio
async def test_async_list_subjects(async_dummy_client, context, async_paginator_factory):
    context.set_default_study_key("S1")
    ep = subjects.SubjectsEndpoint(async_dummy_client, context, async_client=async_dummy_client)
    captured = async_paginator_factory([{"subjectKey": "x"}])
    result = await ep.async_list()
    assert captured["path"] == "/api/v1/edc/studies/S1/subjects"
    assert isinstance(result[0], Subject)


@pytest.mark.asyncio
async def test_async_list_users(async_dummy_client, context, async_paginator_factory):
    ep = users.UsersEndpoint(async_dummy_client, context, async_client=async_dummy_client)
    captured = async_paginator_factory([{"userId": 1}])
    result = await ep.async_list(study_key="S1", include_inactive=True)
    assert captured["path"] == "/api/v1/edc/studies/S1/users"
    assert captured["params"] == {"includeInactive": "true"}
    assert isinstance(result[0], User)


@pytest.mark.asyncio
async def test_async_list_variables(async_dummy_client, context, async_paginator_factory):
    ep = variables.VariablesEndpoint(async_dummy_client, context, async_client=async_dummy_client)
    captured = async_paginator_factory([{"variableId": 1}])
    result = await ep.async_list(study_key="S1")
    assert captured["path"] == "/api/v1/edc/studies/S1/variables"
    assert isinstance(result[0], Variable)


@pytest.mark.asyncio
async def test_async_list_visits(async_dummy_client, context, async_paginator_factory):
    context.set_default_study_key("S1")
    ep = visits.VisitsEndpoint(async_dummy_client, context, async_client=async_dummy_client)
    captured = async_paginator_factory([{"visitId": 1}])
    result = await ep.async_list(status="x")
    assert captured["path"] == "/api/v1/edc/studies/S1/visits"
    assert isinstance(result[0], Visit)


@pytest.mark.asyncio
async def test_async_get_job(async_dummy_client, context, response_factory):
    ep = jobs.JobsEndpoint(async_dummy_client, context, async_client=async_dummy_client)

    async def fake_get(path):
        assert path == "/api/v1/edc/studies/S1/jobs/B1"
        return response_factory({"jobId": "1"})

    async_dummy_client.get = fake_get
    result = await ep.async_get("S1", "B1")
    assert isinstance(result, JobStatus)


@pytest.mark.asyncio
async def test_async_get_record(monkeypatch, async_dummy_client, context, response_factory):
    ep = records.RecordsEndpoint(async_dummy_client, context, async_client=async_dummy_client)
    called = {}

    async def fake_impl(self, client, paginator, *, study_key=None, **filters):
        called["study_key"] = study_key
        called["filters"] = filters
        return [Record(record_id=1)]

    monkeypatch.setattr(records.RecordsEndpoint, "_list_impl", fake_impl)

    rec = await ep.async_get("S1", 1)

    assert called == {"study_key": "S1", "filters": {"recordId": 1, "refresh": True}}
    assert isinstance(rec, Record)


@pytest.mark.asyncio
async def test_async_get_record_not_found(monkeypatch, async_dummy_client, context, response_factory):
    ep = records.RecordsEndpoint(async_dummy_client, context, async_client=async_dummy_client)

    async def fake_impl(self, client, paginator, *, study_key=None, refresh=False, **filters):
        return []

    monkeypatch.setattr(records.RecordsEndpoint, "_list_impl", fake_impl)

    with pytest.raises(ValueError):
        await ep.async_get("S1", 1)


@pytest.mark.asyncio
async def test_async_create_record(async_dummy_client, context, response_factory, monkeypatch):
    ep = records.RecordsEndpoint(async_dummy_client, context, async_client=async_dummy_client)
    async_dummy_client.post = AsyncMock(return_value=response_factory({"jobId": "1"}))

    monkeypatch.setattr(records.Job, "from_json", lambda d: d)
    job = await ep.async_create("S1", [{"foo": "bar"}], email_notify="user@test")

    async_dummy_client.post.assert_awaited_once_with(
        "/api/v1/edc/studies/S1/records",
        json=[{"foo": "bar"}],
        headers={"x-email-notify": "user@test"},
    )
    assert job == {"jobId": "1"}
