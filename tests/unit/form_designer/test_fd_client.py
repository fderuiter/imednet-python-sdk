import httpx
import pytest

from imednet.form_designer.client import FormDesignerClient
from imednet.form_designer.models import Layout, Page


@pytest.fixture
def mock_layout():
    return Layout(pages=[Page(entities=[])])


def test_save_form_success(mock_layout, respx_mock):
    base_url = "https://test.imednet.com"
    client = FormDesignerClient(base_url, "fake_sessid")

    respx_mock.post(
        f"{base_url}/app/formdez/formdez_save.php",
    ).mock(return_value=httpx.Response(200, json={"success": True}))

    resp = client.save_form("csrf", 1, 1, 1, mock_layout)
    # response.text is returned
    assert '{"success": true}' in resp or "success" in resp

    assert respx_mock.calls.call_count == 1
    req = respx_mock.calls.last.request
    assert "PHPSESSID=fake_sessid" in req.headers["Cookie"]
    assert req.headers["X-Requested-With"] == "XMLHttpRequest"


def test_save_form_server_error(mock_layout, respx_mock):
    base_url = "https://test.imednet.com"
    client = FormDesignerClient(base_url, "fake_sessid")

    respx_mock.post(
        f"{base_url}/app/formdez/formdez_save.php",
    ).mock(return_value=httpx.Response(200, json={"error": "Concurrency Error"}))

    with pytest.raises(ValueError, match="Server Error: Concurrency Error"):
        client.save_form("csrf", 1, 1, 1, mock_layout)


def test_save_form_http_error(mock_layout, respx_mock):
    base_url = "https://test.imednet.com"
    client = FormDesignerClient(base_url, "fake_sessid")

    respx_mock.post(f"{base_url}/app/formdez/formdez_save.php").mock(
        return_value=httpx.Response(500)
    )

    with pytest.raises(httpx.HTTPStatusError):
        client.save_form("csrf", 1, 1, 1, mock_layout)
