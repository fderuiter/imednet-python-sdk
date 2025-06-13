from unittest.mock import AsyncMock

import imednet.endpoints.codings as codings
import imednet.endpoints.forms as forms
import imednet.endpoints.intervals as intervals
import imednet.endpoints.jobs as jobs
import imednet.endpoints.queries as queries
import imednet.endpoints.record_revisions as record_revisions
import imednet.endpoints.records as records
import imednet.endpoints.sites as sites
import imednet.endpoints.subjects as subjects
import imednet.endpoints.users as users
import imednet.endpoints.variables as variables
import imednet.endpoints.visits as visits
import pytest
from imednet.models.codings import Coding
from imednet.models.forms import Form
from imednet.models.intervals import Interval
from imednet.models.jobs import JobStatus
from imednet.models.queries import Query
from imednet.models.record_revisions import RecordRevision
from imednet.models.records import Record
from imednet.models.sites import Site
from imednet.models.subjects import Subject
from imednet.models.users import User
from imednet.models.variables import Variable
from imednet.models.visits import Visit


@pytest.mark.asyncio
async def test_async_list_records(
    dummy_client, context, async_paginator_factory, patch_build_filter
):
    ep = records.RecordsEndpoint(dummy_client, context, async_client=dummy_client)
    captured = async_paginator_factory(records, [{"recordId": 1}])
    filter_capture = patch_build_filter(records)
    result = await ep.async_list(study_key="S1", record_data_filter="x")
    assert captured["path"] == "/api/v1/edc/studies/S1/records"
    assert captured["params"] == {"filter": "FILTERED", "recordDataFilter": "x"}
    assert filter_capture["filters"] == {"studyKey": "S1"}
    assert isinstance(result[0], Record)


@pytest.mark.asyncio
async def test_async_list_codings(dummy_client, context, async_paginator_factory):
    ep = codings.CodingsEndpoint(dummy_client, context, async_client=dummy_client)
    captured = async_paginator_factory(codings, [{"codingId": 1}])
    result = await ep.async_list(study_key="S1")
    assert captured["path"] == "/api/v1/edc/studies/S1/codings"
    assert isinstance(result[0], Coding)


@pytest.mark.asyncio
async def test_async_list_forms(dummy_client, context, async_paginator_factory):
    context.set_default_study_key("S1")
    ep = forms.FormsEndpoint(dummy_client, context, async_client=dummy_client)
    captured = async_paginator_factory(forms, [{"formId": 1}])
    result = await ep.async_list()
    assert captured["path"] == "/api/v1/edc/studies/S1/forms"
    assert isinstance(result[0], Form)


@pytest.mark.asyncio
async def test_async_list_intervals(dummy_client, context, async_paginator_factory):
    context.set_default_study_key("S1")
    ep = intervals.IntervalsEndpoint(dummy_client, context, async_client=dummy_client)
    captured = async_paginator_factory(intervals, [{"intervalId": 1}])
    result = await ep.async_list()
    assert captured["path"] == "/api/v1/edc/studies/S1/intervals"
    assert isinstance(result[0], Interval)


@pytest.mark.asyncio
async def test_async_list_queries(dummy_client, context, async_paginator_factory):
    context.set_default_study_key("S1")
    ep = queries.QueriesEndpoint(dummy_client, context, async_client=dummy_client)
    captured = async_paginator_factory(queries, [{"annotationId": 1}])
    result = await ep.async_list(status="new")
    assert captured["path"] == "/api/v1/edc/studies/S1/queries"
    assert isinstance(result[0], Query)


@pytest.mark.asyncio
async def test_async_list_record_revisions(dummy_client, context, async_paginator_factory):
    context.set_default_study_key("S1")
    ep = record_revisions.RecordRevisionsEndpoint(
        dummy_client,
        context,
        async_client=dummy_client,
    )
    captured = async_paginator_factory(record_revisions, [{"recordRevisionId": 1}])
    result = await ep.async_list(status="x")
    assert captured["path"] == "/api/v1/edc/studies/S1/recordRevisions"
    assert isinstance(result[0], RecordRevision)


@pytest.mark.asyncio
async def test_async_list_sites(dummy_client, context, async_paginator_factory):
    ep = sites.SitesEndpoint(dummy_client, context, async_client=dummy_client)
    captured = async_paginator_factory(sites, [{"siteId": 1}])
    result = await ep.async_list(study_key="S1")
    assert captured["path"] == "/api/v1/edc/studies/S1/sites"
    assert isinstance(result[0], Site)


@pytest.mark.asyncio
async def test_async_list_subjects(dummy_client, context, async_paginator_factory):
    context.set_default_study_key("S1")
    ep = subjects.SubjectsEndpoint(dummy_client, context, async_client=dummy_client)
    captured = async_paginator_factory(subjects, [{"subjectKey": "x"}])
    result = await ep.async_list()
    assert captured["path"] == "/api/v1/edc/studies/S1/subjects"
    assert isinstance(result[0], Subject)


@pytest.mark.asyncio
async def test_async_list_users(dummy_client, context, async_paginator_factory):
    ep = users.UsersEndpoint(dummy_client, context, async_client=dummy_client)
    captured = async_paginator_factory(users, [{"userId": 1}])
    result = await ep.async_list(study_key="S1", include_inactive=True)
    assert captured["path"] == "/api/v1/edc/studies/S1/users"
    assert captured["params"] == {"includeInactive": "true"}
    assert isinstance(result[0], User)


@pytest.mark.asyncio
async def test_async_list_variables(dummy_client, context, async_paginator_factory):
    ep = variables.VariablesEndpoint(dummy_client, context, async_client=dummy_client)
    captured = async_paginator_factory(variables, [{"variableId": 1}])
    result = await ep.async_list(study_key="S1")
    assert captured["path"] == "/api/v1/edc/studies/S1/variables"
    assert isinstance(result[0], Variable)


@pytest.mark.asyncio
async def test_async_list_visits(dummy_client, context, async_paginator_factory):
    context.set_default_study_key("S1")
    ep = visits.VisitsEndpoint(dummy_client, context, async_client=dummy_client)
    captured = async_paginator_factory(visits, [{"visitId": 1}])
    result = await ep.async_list(status="x")
    assert captured["path"] == "/api/v1/edc/studies/S1/visits"
    assert isinstance(result[0], Visit)


@pytest.mark.asyncio
async def test_async_get_job(dummy_client, context, response_factory):
    ep = jobs.JobsEndpoint(dummy_client, context, async_client=dummy_client)

    async def fake_get(path):
        assert path == "/api/v1/edc/studies/S1/jobs/B1"
        return response_factory({"jobId": "1"})

    dummy_client.get = fake_get
    result = await ep.async_get("S1", "B1")
    assert isinstance(result, JobStatus)


@pytest.mark.asyncio
async def test_async_get_record(dummy_client, context, monkeypatch):
    ep = records.RecordsEndpoint(dummy_client, context, async_client=dummy_client)
    captured = {}

    async def fake_list(study_key=None, refresh=False, **filters):
        captured["study_key"] = study_key
        captured["refresh"] = refresh
        captured["filters"] = filters
        return [Record(record_id=1)]

    monkeypatch.setattr(ep, "async_list", fake_list)

    rec = await ep.async_get("S1", 1)

    assert captured == {"study_key": "S1", "refresh": True, "filters": {"recordId": 1}}
    assert isinstance(rec, Record)


@pytest.mark.asyncio
async def test_async_get_record_not_found(dummy_client, context, monkeypatch):
    ep = records.RecordsEndpoint(dummy_client, context, async_client=dummy_client)

    async def fake_list(**kwargs):
        return []

    monkeypatch.setattr(ep, "async_list", fake_list)

    with pytest.raises(ValueError):
        await ep.async_get("S1", 1)


@pytest.mark.asyncio
async def test_async_create_record(dummy_client, context, response_factory, monkeypatch):
    ep = records.RecordsEndpoint(dummy_client, context, async_client=dummy_client)
    dummy_client.post = AsyncMock(return_value=response_factory({"jobId": "1"}))

    monkeypatch.setattr(records.Job, "from_json", lambda d: d)
    job = await ep.async_create("S1", [{"foo": "bar"}], email_notify="user@test")

    dummy_client.post.assert_awaited_once_with(
        "/api/v1/edc/studies/S1/records",
        json=[{"foo": "bar"}],
        headers={"x-email-notify": "user@test"},
    )
    assert job == {"jobId": "1"}
