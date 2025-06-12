import re
import asyncio

import httpx
import pytest
import respx

from imednet.core.exceptions import NotFoundError


@pytest.mark.asyncio
async def test_client_get_success(client, respx_mock):
    respx_mock.get("/hello").mock(return_value=httpx.Response(200, json={"ok": True}))
    response = client.get("/hello")
    assert response.json() == {"ok": True}
    assert respx_mock.calls.call_count == 1


def test_client_get_not_found(client, respx_mock):
    respx_mock.get("/missing").mock(return_value=httpx.Response(404, json={"detail": "no"}))
    with pytest.raises(NotFoundError):
        client.get("/missing")
    assert respx_mock.calls.call_count == 1


@pytest.mark.asyncio
async def test_studies_list_paginated(studies_endpoint, study_json):
    page1 = {"data": [study_json], "pagination": {"totalPages": 2}}
    page2 = {"data": [study_json], "pagination": {"totalPages": 2}}
    pattern = re.compile(r"/api/v1/edc/studies.*")
    with respx.mock(base_url="https://api.test") as respx_mock:
        route = respx_mock.get(pattern)
        route.side_effect = [
            httpx.Response(200, json=page1),
            httpx.Response(200, json=page2),
        ]
        studies = studies_endpoint.list()
        assert respx_mock.calls.call_count == 2
        assert len(studies) == 2
        assert studies[0].study_key == "STUDY1"
