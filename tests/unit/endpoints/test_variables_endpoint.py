from unittest.mock import MagicMock

import imednet.endpoints.variables as variables
import pytest
from imednet.models.variables import Variable


def test_list_requires_study_key_page_size(
    dummy_client, context, paginator_factory, patch_build_filter
):
    ep = variables.VariablesEndpoint(dummy_client, context)
    capture = paginator_factory(variables, [{"variableId": 1}])
    patch = patch_build_filter(variables)

    with pytest.raises(KeyError):
        ep.list()

    result = ep.list(study_key="S1", name="x")

    assert capture["path"] == "/api/v1/edc/studies/S1/variables"
    assert capture["page_size"] == 500
    assert capture["params"] == {"filter": "FILTERED"}
    assert patch["filters"] == {"name": "x"}
    assert isinstance(result[0], Variable)


def test_get_not_found(dummy_client, context, response_factory):
    ep = variables.VariablesEndpoint(dummy_client, context)
    dummy_client.get.return_value = response_factory({"data": []})
    with pytest.raises(ValueError):
        ep.get("S1", 1)


def test_list_caches_by_study_key(dummy_client, context, paginator_factory):
    ep = variables.VariablesEndpoint(dummy_client, context)
    capture = paginator_factory(variables, [{"variableId": 1}])

    first = ep.list(study_key="S1")
    second = ep.list(study_key="S1")

    assert capture["count"] == 1
    assert first == second

    ep.list(study_key="S2")

    assert capture["count"] == 2


def test_list_refresh_bypasses_cache(dummy_client, context, paginator_factory):
    ep = variables.VariablesEndpoint(dummy_client, context)
    capture = paginator_factory(variables, [{"variableId": 1}])

    ep.list(study_key="S1")
    ep.list(study_key="S1", refresh=True)

    assert capture["count"] == 2


@pytest.mark.asyncio
async def test_async_list_caches(async_dummy_client, context, response_factory):
    ep = variables.VariablesEndpoint(MagicMock(), context, async_client=async_dummy_client)
    async_dummy_client.get.return_value = response_factory(
        {"data": [{"variableId": 1}], "pagination": {"totalPages": 1}}
    )

    first = await ep.async_list(study_key="S1")
    second = await ep.async_list(study_key="S1")

    assert async_dummy_client.get.call_count == 1
    assert first == second


@pytest.mark.asyncio
async def test_async_list_refresh(async_dummy_client, context, response_factory):
    ep = variables.VariablesEndpoint(MagicMock(), context, async_client=async_dummy_client)
    async_dummy_client.get.return_value = response_factory(
        {"data": [{"variableId": 1}], "pagination": {"totalPages": 1}}
    )

    await ep.async_list(study_key="S1")
    await ep.async_list(study_key="S1", refresh=True)

    assert async_dummy_client.get.call_count == 2
