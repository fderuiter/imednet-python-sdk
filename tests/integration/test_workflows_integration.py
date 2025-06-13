import re
import time

import httpx
import pytest
import respx
from imednet.sdk import ImednetSDK
from imednet.workflows.data_extraction import DataExtractionWorkflow
from imednet.workflows.query_management import QueryManagementWorkflow
from imednet.workflows.record_update import RecordUpdateWorkflow
from imednet.workflows.subject_data import SubjectDataWorkflow


@respx.mock
def test_data_extraction_filters():
    sdk = ImednetSDK(api_key="k", security_key="s", base_url="https://api.test")
    respx.get("https://api.test/api/v1/edc/studies/ST/variables").respond(json={"data": []})
    respx.get("https://api.test/api/v1/edc/studies/ST/subjects").respond(
        json={"data": [{"subjectKey": "SUB1"}]}
    )
    respx.get("https://api.test/api/v1/edc/studies/ST/visits").respond(
        json={"data": [{"visitId": 1, "subjectKey": "SUB1"}]}
    )
    respx.get("https://api.test/api/v1/edc/studies/ST/records").respond(
        json={
            "data": [
                {"recordId": 1, "subjectKey": "SUB1", "visitId": 1, "formId": 10},
                {"recordId": 2, "subjectKey": "SUB1", "visitId": 2, "formId": 10},
            ]
        }
    )

    wf = DataExtractionWorkflow(sdk)
    recs = wf.extract_records_by_criteria(
        "ST",
        record_filter={"form_id": 10},
        subject_filter={"status": "active"},
        visit_filter={"visit_id": 1},
    )

    assert [r.record_id for r in recs] == [1]


@respx.mock
def test_record_update_submit_and_wait(monkeypatch: pytest.MonkeyPatch):
    sdk = ImednetSDK(api_key="k", security_key="s", base_url="https://api.test")
    respx.get(re.compile("https://api.test/api/v1/edc/studies/ST/variables.*")).respond(
        json={"data": []}
    )
    respx.post("https://api.test/api/v1/edc/studies/ST/records").respond(
        json={"batchId": "B1", "state": "PROCESSING"}
    )
    route = respx.get("https://api.test/api/v1/edc/studies/ST/jobs/B1").mock(
        side_effect=[
            httpx.Response(200, json={"batchId": "B1", "state": "PROCESSING"}),
            httpx.Response(200, json={"batchId": "B1", "state": "COMPLETED"}),
        ]
    )
    monkeypatch.setattr(time, "sleep", lambda *_: None)

    wf = RecordUpdateWorkflow(sdk)
    job = wf.create_or_update_records(
        "ST", [{"formKey": "F1", "data": {"x": 1}}], wait_for_completion=True, poll_interval=0
    )

    assert job.state == "COMPLETED"
    assert route.call_count == 2


@respx.mock
def test_subject_data_aggregation():
    sdk = ImednetSDK(api_key="k", security_key="s", base_url="https://api.test")
    respx.get("https://api.test/api/v1/edc/studies/ST/subjects").respond(
        json={"data": [{"subjectKey": "SUB1"}]}
    )
    respx.get("https://api.test/api/v1/edc/studies/ST/visits").respond(
        json={"data": [{"visitId": 1, "subjectKey": "SUB1"}]}
    )
    respx.get("https://api.test/api/v1/edc/studies/ST/records").respond(
        json={"data": [{"recordId": 1, "subjectKey": "SUB1", "visitId": 1, "formId": 10}]}
    )
    respx.get("https://api.test/api/v1/edc/studies/ST/queries").respond(
        json={"data": [{"queryComments": [{"sequence": 1, "closed": False}]}]}
    )

    wf = SubjectDataWorkflow(sdk)
    data = wf.get_all_subject_data("ST", "SUB1")

    assert data.subject_details.subject_key == "SUB1"
    assert len(data.visits) == 1
    assert len(data.records) == 1
    assert len(data.queries) == 1


@respx.mock
def test_query_management_counts():
    sdk = ImednetSDK(api_key="k", security_key="s", base_url="https://api.test")
    respx.get("https://api.test/api/v1/edc/studies/ST/queries").respond(
        json={
            "data": [
                {"queryComments": [{"sequence": 1, "closed": False}]},
                {"queryComments": [{"sequence": 1, "closed": True}]},
                {"queryComments": []},
            ]
        }
    )

    wf = QueryManagementWorkflow(sdk)
    counts = wf.get_query_state_counts("ST")

    assert counts == {"open": 1, "closed": 1, "unknown": 1}


@respx.mock
def test_data_extraction_no_matching_subjects() -> None:
    sdk = ImednetSDK(api_key="k", security_key="s", base_url="https://api.test")
    subjects_route = respx.get("https://api.test/api/v1/edc/studies/ST/subjects").respond(
        json={"data": []}
    )
    visits_route = respx.get("https://api.test/api/v1/edc/studies/ST/visits").mock(
        side_effect=AssertionError("visits should not be called")
    )
    records_route = respx.get("https://api.test/api/v1/edc/studies/ST/records").mock(
        side_effect=AssertionError("records should not be called")
    )

    wf = DataExtractionWorkflow(sdk)
    recs = wf.extract_records_by_criteria("ST", subject_filter={"status": "active"})

    assert recs == []
    assert subjects_route.called
    assert not visits_route.called
    assert not records_route.called


@respx.mock
def test_record_update_timeout(monkeypatch: pytest.MonkeyPatch) -> None:
    sdk = ImednetSDK(api_key="k", security_key="s", base_url="https://api.test")
    respx.get(re.compile("https://api.test/api/v1/edc/studies/ST/variables.*")).respond(
        json={"data": []}
    )
    respx.post("https://api.test/api/v1/edc/studies/ST/records").respond(
        json={"batchId": "B1", "state": "PROCESSING"}
    )
    respx.get("https://api.test/api/v1/edc/studies/ST/jobs/B1").respond(
        json={"batchId": "B1", "state": "PROCESSING"}
    )

    counter = {"v": 0}

    def monotonic() -> int:
        counter["v"] += 1
        return counter["v"]

    monkeypatch.setattr(time, "monotonic", monotonic)
    monkeypatch.setattr(time, "sleep", lambda *_: None)

    wf = RecordUpdateWorkflow(sdk)
    with pytest.raises(TimeoutError):
        wf.create_or_update_records(
            "ST",
            [{"formKey": "F1", "data": {"x": 1}}],
            wait_for_completion=True,
            timeout=1,
            poll_interval=0,
        )


@respx.mock
def test_get_open_queries() -> None:
    sdk = ImednetSDK(api_key="k", security_key="s", base_url="https://api.test")
    respx.get("https://api.test/api/v1/edc/studies/ST/queries").respond(
        json={
            "data": [
                {"queryComments": [{"sequence": 1, "closed": True}]},
                {"queryComments": [{"sequence": 1, "closed": False}]},
            ]
        }
    )

    wf = QueryManagementWorkflow(sdk)
    queries = wf.get_open_queries("ST")

    assert len(queries) == 1
    assert not queries[0].query_comments[0].closed
