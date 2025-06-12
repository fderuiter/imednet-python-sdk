import pytest

import imednet.endpoints.records as records
from imednet.models.records import Record
from imednet.models.jobs import Job


def test_list_builds_path_filters_and_data_filter(dummy_client, context, paginator_factory, patch_build_filter):
    ep = records.RecordsEndpoint(dummy_client, context)
    captured = paginator_factory(records, [{"recordId": 1}])
    filter_capture = patch_build_filter(records)

    result = ep.list(study_key="S1", record_data_filter="age>10", status="open")

    assert captured["path"] == "/api/v1/edc/studies/S1/records"
    assert captured["params"] == {"filter": "FILTERED", "recordDataFilter": "age>10"}
    assert filter_capture["filters"] == {"status": "open", "studyKey": "S1"}
    assert isinstance(result[0], Record)


def test_get_success(dummy_client, context, response_factory):
    ep = records.RecordsEndpoint(dummy_client, context)
    dummy_client.get.return_value = response_factory({"data": [{"recordId": 1}]})

    res = ep.get("S1", 1)

    dummy_client.get.assert_called_once_with("/api/v1/edc/studies/S1/records/1")
    assert isinstance(res, Record)


def test_get_not_found(dummy_client, context, response_factory):
    ep = records.RecordsEndpoint(dummy_client, context)
    dummy_client.get.return_value = response_factory({"data": []})
    with pytest.raises(ValueError):
        ep.get("S1", 1)


def test_create_sends_headers_and_parses_job(dummy_client, context, response_factory, monkeypatch):
    ep = records.RecordsEndpoint(dummy_client, context)
    dummy_client.post.return_value = response_factory({"jobId": "1"})
    called = {}

    def fake_from_json(data):
        called["data"] = data
        return "JOB"

    monkeypatch.setattr(records.Job, "from_json", staticmethod(fake_from_json))

    res = ep.create("S1", [{"foo": "bar"}], email_notify=True)

    dummy_client.post.assert_called_once_with(
        "/api/v1/edc/studies/S1/records",
        json=[{"foo": "bar"}],
        headers={"x-email-notify": "true"},
    )
    assert called["data"] == {"jobId": "1"}
    assert res == "JOB"
