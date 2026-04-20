import json

import httpx
import pytest
import respx

from imednet.errors import ApiError
from imednet.form_designer.client import FormDesignerClient
from imednet.form_designer.models import Layout


@pytest.fixture
def form_designer_client():
    return FormDesignerClient(base_url="https://test.imednet.com", phpsessid="test_session")


@pytest.fixture
def empty_layout():
    return Layout(pages=[])


@respx.mock
def test_save_form_explicit_json_error(form_designer_client, empty_layout):
    """
    Test that the client correctly parses explicit JSON API errors
    (e.g., {"error": "..."}) returned with a 200 OK status code.
    """
    url = "https://test.imednet.com/app/formdez/formdez_save.php"

    # Mock a 200 OK response with a JSON error payload
    respx.post(url).respond(status_code=200, json={"error": "Invalid form configuration"})

    with pytest.raises(ApiError) as exc_info:
        form_designer_client.save_form(
            csrf_key="test_csrf",
            form_id=1,
            community_id=1,
            revision=1,
            layout=empty_layout,
        )

    assert "Server Error: Invalid form configuration" in str(exc_info.value)
    assert exc_info.value.status_code == 200


@respx.mock
def test_save_form_invalid_json_fallback(form_designer_client, empty_layout):
    """
    Test that the client correctly handles fallback behavior when the
    legacy endpoint returns non-JSON (e.g., HTML) instead of JSON on error.
    """
    url = "https://test.imednet.com/app/formdez/formdez_save.php"

    # Legacy endpoints may sometimes return HTML instead of JSON for errors
    html_error = "<html><body>Fatal PHP Error</body></html>"

    # Mock a 200 OK response with HTML content
    respx.post(url).respond(
        status_code=200,
        content=html_error.encode("utf-8"),
        headers={"Content-Type": "text/html"}
    )

    with pytest.raises(ApiError) as exc_info:
        form_designer_client.save_form(
            csrf_key="test_csrf",
            form_id=1,
            community_id=1,
            revision=1,
            layout=empty_layout,
        )

    # Verify the fallback handling propagates the raw text and original status code
    assert html_error in str(exc_info.value)
    assert exc_info.value.status_code == 200
    # Verify the fallback was triggered due to JSONDecodeError
    assert isinstance(exc_info.value.__cause__, json.JSONDecodeError)
