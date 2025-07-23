import asyncio
from unittest.mock import AsyncMock

import pytest

import imednet.endpoints.records as records
from imednet.core.exceptions import ValidationError
from imednet.models.records import Record
from imednet.models.variables import Variable
from imednet.validation.cache import SchemaCache


@pytest.mark.parametrize("use_async", [False, True])
def test_list_builds_path_filters_and_data_filter(
    dummy_client,
    context,
    paginator_factory,
    patch_build_filter,
    use_async,
    async_paginator_factory,
):
    ep = records.RecordsEndpoint(
        dummy_client, context, async_client=dummy_client if use_async else None
    )
    factory = async_paginator_factory if use_async else paginator_factory
    captured = factory(records, [{"recordId": 1}])
    filter_capture = patch_build_filter(records)

    if use_async:
        result = asyncio.run(
            ep.async_list(
                study_key="S1",
                record_data_filter="age>10",
                status="open",
            )
        )
    else:
        result = ep.list(
            study_key="S1",
            record_data_filter="age>10",
            status="open",
        )

    assert captured["path"] == "/api/v1/edc/studies/S1/records"
    assert captured["params"] == {"filter": "FILTERED", "recordDataFilter": "age>10"}
    assert filter_capture["filters"] == {"status": "open", "studyKey": "S1"}
    assert isinstance(result[0], Record)


@pytest.mark.parametrize("use_async", [False, True])
def test_get_success(monkeypatch, dummy_client, context, use_async):
    ep = records.RecordsEndpoint(
        dummy_client, context, async_client=dummy_client if use_async else None
    )
    called = {}

    if use_async:

        async def fake_impl(self, client, paginator, *, study_key=None, **filters):
            called["study_key"] = study_key
            called["filters"] = filters
            return [Record(record_id=1)]

    else:

        def fake_impl(self, client, paginator, *, study_key=None, **filters):
            called["study_key"] = study_key
            called["filters"] = filters
            return [Record(record_id=1)]

    monkeypatch.setattr(records.RecordsEndpoint, "_list_impl", fake_impl)

    if use_async:
        res = asyncio.run(ep.async_get("S1", 1))
    else:
        res = ep.get("S1", 1)

    assert called == {"study_key": "S1", "filters": {"recordId": 1, "refresh": True}}
    assert isinstance(res, Record)


@pytest.mark.parametrize("use_async", [False, True])
def test_get_not_found(monkeypatch, dummy_client, context, use_async):
    ep = records.RecordsEndpoint(
        dummy_client, context, async_client=dummy_client if use_async else None
    )

    if use_async:

        async def fake_impl(self, client, paginator, *, study_key=None, refresh=False, **filters):
            return []

    else:

        def fake_impl(self, client, paginator, *, study_key=None, refresh=False, **filters):
            return []

    monkeypatch.setattr(records.RecordsEndpoint, "_list_impl", fake_impl)

    with pytest.raises(ValueError):
        if use_async:
            asyncio.run(ep.async_get("S1", 1))
        else:
            ep.get("S1", 1)


@pytest.mark.parametrize("use_async", [False, True])
def test_create_sends_headers_and_parses_job(
    dummy_client, context, response_factory, monkeypatch, use_async
):
    ep = records.RecordsEndpoint(
        dummy_client, context, async_client=dummy_client if use_async else None
    )
    if use_async:
        dummy_client.post = AsyncMock(return_value=response_factory({"jobId": "1"}))
    else:
        dummy_client.post.return_value = response_factory({"jobId": "1"})
    called = {}

    def fake_from_json(data):
        called["data"] = data
        return "JOB"

    monkeypatch.setattr(records.Job, "from_json", staticmethod(fake_from_json))

    if use_async:
        res = asyncio.run(ep.async_create("S1", [{"foo": "bar"}], email_notify=True))
    else:
        res = ep.create("S1", [{"foo": "bar"}], email_notify=True)

    if use_async:
        dummy_client.post.assert_awaited_once_with(
            "/api/v1/edc/studies/S1/records",
            json=[{"foo": "bar"}],
            headers={"x-email-notify": "true"},
        )
    else:
        dummy_client.post.assert_called_once_with(
            "/api/v1/edc/studies/S1/records",
            json=[{"foo": "bar"}],
            headers={"x-email-notify": "true"},
        )
    assert called["data"] == {"jobId": "1"}
    assert res == "JOB"


@pytest.mark.parametrize("use_async", [False, True])
def test_create_validates_data(dummy_client, context, response_factory, use_async):
    ep = records.RecordsEndpoint(
        dummy_client, context, async_client=dummy_client if use_async else None
    )
    schema = SchemaCache()
    var = Variable(variable_name="age", variable_type="integer", form_id=1, form_key="F1")
    schema._form_variables = {"F1": {"age": var}}
    schema._form_id_to_key = {1: "F1"}

    if use_async:
        dummy_client.post = AsyncMock(return_value=response_factory({"jobId": "1"}))
    else:
        dummy_client.post.return_value = response_factory({"jobId": "1"})

    # invalid key
    with pytest.raises(ValidationError):
        if use_async:
            asyncio.run(
                ep.async_create(
                    "S1",
                    [{"formKey": "F1", "data": {"bad": 1}}],
                    schema=schema,
                )
            )
        else:
            ep.create("S1", [{"formKey": "F1", "data": {"bad": 1}}], schema=schema)
    dummy_client.post.assert_not_called()

    # valid
    if use_async:
        asyncio.run(
            ep.async_create(
                "S1",
                [{"formKey": "F1", "data": {"age": 5}}],
                schema=schema,
            )
        )
        dummy_client.post.assert_awaited()
    else:
        ep.create("S1", [{"formKey": "F1", "data": {"age": 5}}], schema=schema)
        dummy_client.post.assert_called_once()
