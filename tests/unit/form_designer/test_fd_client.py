import pytest
import responses

from imednet.form_designer.client import FormDesignerClient
from imednet.form_designer.models import Layout, Page


@pytest.fixture
def mock_layout():
    return Layout(pages=[Page(entities=[])])


@responses.activate
def test_save_form_success(mock_layout):
    base_url = "https://test.imednet.com"
    client = FormDesignerClient(base_url, "fake_sessid")

    responses.add(
        responses.POST,
        f"{base_url}/app/formdez/formdez_save.php",
        json={"success": True},
        status=200,
    )

    resp = client.save_form("csrf", 1, 1, 1, mock_layout)
    # responses.json returns json body as text if accessed via .text? No, requests.text returns str.
    assert '{"success": True}' in resp or "success" in resp

    # Check headers
    req_headers = responses.calls[0].request.headers
    assert req_headers["Cookie"] == "PHPSESSID=fake_sessid"
    assert req_headers["X-Requested-With"] == "XMLHttpRequest"


@responses.activate
def test_save_form_server_error(mock_layout):
    base_url = "https://test.imednet.com"
    client = FormDesignerClient(base_url, "fake_sessid")

    responses.add(
        responses.POST,
        f"{base_url}/app/formdez/formdez_save.php",
        json={"error": "Concurrency Error"},
        status=200,
    )

    with pytest.raises(ValueError, match="Server Error: Concurrency Error"):
        client.save_form("csrf", 1, 1, 1, mock_layout)


@responses.activate
def test_save_form_http_error(mock_layout):
    base_url = "https://test.imednet.com"
    client = FormDesignerClient(base_url, "fake_sessid")

    responses.add(responses.POST, f"{base_url}/app/formdez/formdez_save.php", status=500)

    from requests.exceptions import HTTPError

    with pytest.raises(HTTPError):
        client.save_form("csrf", 1, 1, 1, mock_layout)
