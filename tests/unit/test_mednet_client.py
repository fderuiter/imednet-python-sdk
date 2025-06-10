from __future__ import annotations

import pytest
import responses
from imednet.mednet_client import Form, MednetApiError, MednetClient, Variable


@responses.activate
def test_get_forms_success() -> None:
    client = MednetClient("S1", headers={"Authorization": "t"})
    responses.add(
        responses.GET,
        "https://api.imednet.com/v2/studies/S1/forms",
        json={"forms": [{"id": 1, "name": "F1"}]},
        status=200,
    )
    forms = client.get_forms()
    assert forms == [Form(id=1, name="F1")]


@responses.activate
def test_get_forms_401_error() -> None:
    client = MednetClient("S1", headers={})
    responses.add(
        responses.GET,
        "https://api.imednet.com/v2/studies/S1/forms",
        json={"detail": "bad"},
        status=401,
    )
    with pytest.raises(MednetApiError):
        client.get_forms()


def test_get_forms_stub() -> None:
    client = MednetClient("S1", headers={})
    forms = client.get_forms(test_mode=True)
    assert len(forms) == 2
    assert forms[0].id == 1


@responses.activate
def test_request_retries(monkeypatch: pytest.MonkeyPatch) -> None:
    sleep_times: list[float] = []
    monkeypatch.setattr("time.sleep", lambda s: sleep_times.append(s))
    client = MednetClient("S1", headers={})
    responses.add(
        responses.GET,
        "https://api.imednet.com/v2/studies/S1/forms",
        status=500,
    )
    responses.add(
        responses.GET,
        "https://api.imednet.com/v2/studies/S1/forms",
        json={"forms": []},
        status=200,
    )
    forms = client.get_forms()
    assert forms == []
    assert sleep_times  # ensured backoff triggered


@responses.activate
def test_get_variables_pagination() -> None:
    client = MednetClient("S1", headers={})
    responses.add(
        responses.GET,
        "https://api.imednet.com/v2/forms/1/variables",
        json={"variables": [{"id": 1, "name": "v1"}], "nextPageToken": "abc"},
        status=200,
    )
    responses.add(
        responses.GET,
        "https://api.imednet.com/v2/forms/1/variables",
        match=[responses.matchers.query_param_matcher({"pageToken": "abc"})],
        json={"variables": [{"id": 2, "name": "v2"}]},
        status=200,
    )
    variables = client.get_variables(1)
    assert variables == [Variable(id=1, name="v1"), Variable(id=2, name="v2")]
