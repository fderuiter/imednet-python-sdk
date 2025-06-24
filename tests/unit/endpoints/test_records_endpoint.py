import imednet.endpoints.records as records
import pytest
from imednet.core.exceptions import ValidationError
from imednet.models.records import Record
from imednet.models.variables import Variable
from imednet.validation.schema import SchemaCache


def test_list_builds_path_filters_and_data_filter(
    dummy_client, context, paginator_factory, patch_build_filter
):
    ep = records.RecordsEndpoint(dummy_client, context)
    captured = paginator_factory(records, [{"recordId": 1}])
    filter_capture = patch_build_filter(records)

    result = ep.list(
        study_key="S1",
        record_data_filter="age>10",
        status="open",
    )

    assert captured["path"] == "/api/v1/edc/studies/S1/records"
    assert captured["params"] == {"filter": "FILTERED", "recordDataFilter": "age>10"}
    assert filter_capture["filters"] == {"status": "open", "studyKey": "S1"}
    assert isinstance(result[0], Record)


def test_get_success(monkeypatch, dummy_client, context):
    ep = records.RecordsEndpoint(dummy_client, context)
    called = {}

    def fake_impl(self, client, paginator, *, study_key=None, **filters):
        called["study_key"] = study_key
        called["filters"] = filters
        return [Record(record_id=1)]

    monkeypatch.setattr(records.RecordsEndpoint, "_list_impl", fake_impl)

    res = ep.get("S1", 1)

    assert called == {"study_key": "S1", "filters": {"recordId": 1}}
    assert isinstance(res, Record)


def test_get_not_found(monkeypatch, dummy_client, context):
    ep = records.RecordsEndpoint(dummy_client, context)

    def fake_impl(self, client, paginator, *, study_key=None, refresh=False, **filters):
        return []

    monkeypatch.setattr(records.RecordsEndpoint, "_list_impl", fake_impl)

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


def test_create_validates_data(dummy_client, context, response_factory):
    ep = records.RecordsEndpoint(dummy_client, context)
    schema = SchemaCache()
    var = Variable(variable_name="age", variable_type="integer", form_id=1, form_key="F1")
    schema._form_variables = {"F1": {"age": var}}
    schema._form_id_to_key = {1: "F1"}

    dummy_client.post.return_value = response_factory({"jobId": "1"})

    # invalid key
    with pytest.raises(ValidationError):
        ep.create("S1", [{"formKey": "F1", "data": {"bad": 1}}], schema=schema)
    dummy_client.post.assert_not_called()

    # valid
    ep.create("S1", [{"formKey": "F1", "data": {"age": 5}}], schema=schema)
    dummy_client.post.assert_called_once()
