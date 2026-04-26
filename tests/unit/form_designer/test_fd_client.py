import httpx
import pytest

from imednet.errors import ApiError, ClientError
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

    with pytest.raises(ApiError, match="Server Error: Concurrency Error"):
        client.save_form("csrf", 1, 1, 1, mock_layout)


def test_save_form_http_error(mock_layout, respx_mock):
    base_url = "https://test.imednet.com"
    client = FormDesignerClient(base_url, "fake_sessid")

    respx_mock.post(f"{base_url}/app/formdez/formdez_save.php").mock(
        return_value=httpx.Response(500)
    )

    with pytest.raises(httpx.HTTPStatusError):
        client.save_form("csrf", 1, 1, 1, mock_layout)


def test_save_form_invalid_json_fallback(mock_layout, respx_mock):
    """
    Simulate a legacy PHP endpoint returning HTML instead of JSON.
    The client should catch json.JSONDecodeError and raise ApiError instead of returning text.
    """
    base_url = "https://test.imednet.com"
    client = FormDesignerClient(base_url, "fake_sessid")

    html_response = "<html><body>Error</body></html>"
    respx_mock.post(
        f"{base_url}/app/formdez/formdez_save.php",
    ).mock(return_value=httpx.Response(200, text=html_response))

    with pytest.raises(ApiError) as exc_info:
        client.save_form("csrf", 1, 1, 1, mock_layout)

    assert str(exc_info.value.response) == html_response
    assert exc_info.value.status_code == 200


@pytest.mark.parametrize(
    "csrf,form_id,comm_id,rev,expected_error",
    [
        ("", 1, 1, 1, "CSRF Key cannot be empty."),
        ("   ", 1, 1, 1, "CSRF Key cannot be empty."),
        ("csrf", 0, 1, 1, "Invalid form_id: 0. Must be a positive integer."),
        ("csrf", -1, 1, 1, "Invalid form_id: -1. Must be a positive integer."),
        ("csrf", 1, 0, 1, "Invalid community_id: 0. Must be a positive integer."),
        ("csrf", 1, -1, 1, "Invalid community_id: -1. Must be a positive integer."),
        ("csrf", 1, 1, -1, "Invalid revision: -1. Must be non-negative."),
    ],
)
def test_save_form_validation_sad_paths(mock_layout, csrf, form_id, comm_id, rev, expected_error):
    base_url = "https://test.imednet.com"
    client = FormDesignerClient(base_url, "fake_sessid")

    with pytest.raises(ClientError, match=expected_error):
        client.save_form(csrf, form_id, comm_id, rev, mock_layout)
