import pytest

import imednet.sdk as sdk_mod


@pytest.mark.asyncio
async def test_async_convenience_methods_delegate_to_endpoints(monkeypatch) -> None:
    sdk = sdk_mod.AsyncImednetSDK(
        api_key="key", security_key="secret", base_url="https://example.com"
    )
    calls = {}

    async def fake_studies_async_list(study_key=None, **kw):
        calls["studies"] = kw
        return ["STUDY"]

    async def fake_records_async_list(study_key, record_data_filter=None, **kw):
        calls["records"] = (study_key, record_data_filter, kw)
        return ["REC"]

    async def fake_sites_async_list(study_key, **kw):
        calls["sites"] = (study_key, kw)
        return ["SITE"]

    async def fake_subjects_async_list(study_key, **kw):
        calls["subjects"] = (study_key, kw)
        return ["SUB"]

    async def fake_forms_async_list(study_key, **kw):
        calls["forms"] = (study_key, kw)
        return ["FORM"]

    async def fake_intervals_async_list(study_key, **kw):
        calls["intervals"] = (study_key, kw)
        return ["INT"]

    async def fake_variables_async_list(study_key, **kw):
        calls["variables"] = (study_key, kw)
        return ["VAR"]

    async def fake_visits_async_list(study_key, **kw):
        calls["visits"] = (study_key, kw)
        return ["VIS"]

    async def fake_codings_async_list(study_key, **kw):
        calls["codings"] = (study_key, kw)
        return ["COD"]

    async def fake_queries_async_list(study_key, **kw):
        calls["queries"] = (study_key, kw)
        return ["QUERY"]

    async def fake_record_revisions_async_list(study_key, **kw):
        calls["record_revisions"] = (study_key, kw)
        return ["REV"]

    async def fake_users_async_list(study_key, include_inactive=False):
        calls["users"] = (study_key, include_inactive)
        return ["USER"]

    async def fake_async_get_job(study_key, batch_id):
        calls["job"] = (study_key, batch_id)
        return "JOBOBJ"

    monkeypatch.setattr(sdk.studies, "async_list", fake_studies_async_list)
    monkeypatch.setattr(sdk.records, "async_list", fake_records_async_list)
    monkeypatch.setattr(sdk.sites, "async_list", fake_sites_async_list)
    monkeypatch.setattr(sdk.subjects, "async_list", fake_subjects_async_list)
    monkeypatch.setattr(sdk.forms, "async_list", fake_forms_async_list)
    monkeypatch.setattr(sdk.intervals, "async_list", fake_intervals_async_list)
    monkeypatch.setattr(sdk.variables, "async_list", fake_variables_async_list)
    monkeypatch.setattr(sdk.visits, "async_list", fake_visits_async_list)
    monkeypatch.setattr(sdk.codings, "async_list", fake_codings_async_list)
    monkeypatch.setattr(sdk.queries, "async_list", fake_queries_async_list)
    monkeypatch.setattr(sdk.record_revisions, "async_list", fake_record_revisions_async_list)
    monkeypatch.setattr(sdk.users, "async_list", fake_users_async_list)
    monkeypatch.setattr(sdk.jobs, "async_get", fake_async_get_job)

    assert await sdk.async_get_studies(status="active") == ["STUDY"]
    assert await sdk.async_get_records("S1", record_data_filter="x") == ["REC"]
    assert await sdk.async_get_sites("S1", country="US") == ["SITE"]
    assert await sdk.async_get_subjects("S1", status="new") == ["SUB"]
    assert await sdk.async_get_forms("S1", page=2) == ["FORM"]
    assert await sdk.async_get_intervals("S1") == ["INT"]
    assert await sdk.async_get_variables("S1") == ["VAR"]
    assert await sdk.async_get_visits("S1") == ["VIS"]
    assert await sdk.async_get_codings("S1") == ["COD"]
    assert await sdk.async_get_queries("S1", status="open") == ["QUERY"]
    assert await sdk.async_get_record_revisions("S1") == ["REV"]
    assert await sdk.async_get_users("S1", include_inactive=True) == ["USER"]
    assert await sdk.async_get_job("S1", "B1") == "JOBOBJ"

    assert calls["studies"] == {"status": "active"}
    assert calls["records"] == ("S1", "x", {})
    assert calls["sites"] == ("S1", {"country": "US"})
    assert calls["subjects"] == ("S1", {"status": "new"})
    assert calls["forms"] == ("S1", {"page": 2})
    assert calls["intervals"] == ("S1", {})
    assert calls["variables"] == ("S1", {})
    assert calls["visits"] == ("S1", {})
    assert calls["codings"] == ("S1", {})
    assert calls["queries"] == ("S1", {"status": "open"})
    assert calls["record_revisions"] == ("S1", {})
    assert calls["users"] == ("S1", True)
    assert calls["job"] == ("S1", "B1")


@pytest.mark.asyncio
async def test_async_poll_job_convenience(monkeypatch) -> None:
    sdk = sdk_mod.AsyncImednetSDK(
        api_key="key", security_key="secret", base_url="https://example.com"
    )
    calls = {}

    class FakePoller:
        def __init__(self, get_func, is_async):
            calls["init"] = (get_func, is_async)

        async def run_async(self, study_key, batch_id, interval, timeout):
            calls["run"] = (study_key, batch_id, interval, timeout)
            return "JOBOBJ"

    import imednet.sdk_convenience

    monkeypatch.setattr(imednet.sdk_convenience, "JobPoller", FakePoller)

    assert await sdk.async_poll_job("S1", "B1", interval=10, timeout=100) == "JOBOBJ"
    assert calls["run"] == ("S1", "B1", 10, 100)
    assert calls["init"][1] is True
