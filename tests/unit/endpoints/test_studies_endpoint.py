import imednet.endpoints.studies as studies
import pytest
from imednet.models.studies import Study


def test_list_builds_path_and_filters(
    monkeypatch, dummy_client, context, paginator_factory, patch_build_filter
):
    ep = studies.StudiesEndpoint(dummy_client, context)
    captured = paginator_factory(studies, [{"studyKey": "S1"}])
    filter_capture = patch_build_filter(studies)

    result = ep.list(status="active")

    assert captured["path"] == "/api/v1/edc/studies"
    assert captured["params"] == {"filter": "FILTERED"}
    assert filter_capture["filters"] == {"status": "active"}
    assert isinstance(result[0], Study)


def test_get_success(dummy_client, context, response_factory):
    ep = studies.StudiesEndpoint(dummy_client, context)
    dummy_client.get.return_value = response_factory({"data": [{"studyKey": "S1"}]})

    res = ep.get("S1")

    dummy_client.get.assert_called_once_with("/api/v1/edc/studies/S1")
    assert isinstance(res, Study)


def test_get_not_found(dummy_client, context, response_factory):
    ep = studies.StudiesEndpoint(dummy_client, context)
    dummy_client.get.return_value = response_factory({"data": []})
    with pytest.raises(ValueError):
        ep.get("missing")


def test_list_caches_results(dummy_client, context, paginator_factory):
    ep = studies.StudiesEndpoint(dummy_client, context)
    captured = paginator_factory(studies, [{"studyKey": "S1"}])

    first = ep.list()
    second = ep.list()

    assert captured["count"] == 1
    assert first == second


def test_list_refresh_bypasses_cache(dummy_client, context, paginator_factory):
    ep = studies.StudiesEndpoint(dummy_client, context)
    captured = paginator_factory(studies, [{"studyKey": "S1"}])

    ep.list()
    ep.list(refresh=True)

    assert captured["count"] == 2


@pytest.mark.asyncio
async def test_async_list_caches(dummy_client, async_dummy_client, context, response_factory):
    ep = studies.StudiesEndpoint(dummy_client, context, async_client=async_dummy_client)
    async_dummy_client.get.return_value = response_factory(
        {"data": [{"studyKey": "S1"}], "pagination": {"totalPages": 1}}
    )

    first = await ep.async_list()
    second = await ep.async_list()

    assert async_dummy_client.get.call_count == 1
    assert first == second


@pytest.mark.asyncio
async def test_async_list_refresh(dummy_client, async_dummy_client, context, response_factory):
    ep = studies.StudiesEndpoint(dummy_client, context, async_client=async_dummy_client)
    async_dummy_client.get.return_value = response_factory(
        {"data": [{"studyKey": "S1"}], "pagination": {"totalPages": 1}}
    )

    await ep.async_list()
    await ep.async_list(refresh=True)

    assert async_dummy_client.get.call_count == 2
