import json

import httpx

from .models import Layout


class FormDesignerClient:
    """
    Client for the iMedNet Form Designer endpoint.

    Handles the specific authentication and payload requirements of the legacy
    formdez_save.php endpoint.
    """

    def __init__(self, base_url: str, phpsessid: str, timeout: float = 30.0):
        """
        Initialize the client.

        Args:
            base_url: The base URL of the iMedNet instance (e.g., https://xyz.imednet.com).
            phpsessid: The active PHP session ID from the browser.
            timeout: Request timeout in seconds.
        """
        self.base_url = base_url.rstrip("/")
        self.phpsessid = phpsessid
        self.timeout = timeout
        self.session = httpx.Client(timeout=timeout)

    def save_form(
        self,
        csrf_key: str,
        form_id: int,
        community_id: int,
        revision: int,
        layout: Layout,
    ) -> str:
        """
        Submit the form layout to the server.

        Args:
            csrf_key: The CSRF token (scraped from page).
            form_id: The ID of the form being edited.
            community_id: The study ID.
            revision: The NEXT revision number.
            layout: The Form Layout object.

        Returns:
            The raw response text from the server.

        Raises:
            httpx.HTTPStatusError: If the server returns a non-2xx status code.
            ValueError: If the server returns an error.
        """
        url = f"{self.base_url}/app/formdez/formdez_save.php"

        # Critical Headers
        headers = {
            "Cookie": f"PHPSESSID={self.phpsessid}",
            "X-Requested-With": "XMLHttpRequest",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "User-Agent": "iMedNet-SDK-FormBuilder/1.0",
        }

        # Serialize Layout
        # mode='json' ensures we get a JSON string compatible output
        # by_alias=True might be needed if we defined aliases,
        # but we used direct names matching schema
        layout_json = layout.model_dump_json(exclude_none=True)

        # Construct Payload
        # Note: We use a dict and let requests url-encode it
        payload = {
            "CSRFKey": csrf_key,
            "form_id": str(form_id),
            "community_id": str(community_id),
            "revision": str(revision),
            "layout": layout_json,
            "resubmit": "0",
            "quick_save": "1",
            "__internal_ajax_request": "1",
        }

        response = self.session.post(url, data=payload, headers=headers)

        response.raise_for_status()

        # Check for application-level errors (often returned as 200 OK but with error text)
        # However, the requirement says "Signals the backend to return a JSON response"
        # So we should try to parse it.
        try:
            resp_data = response.json()
            # If it's JSON, it usually contains status info.
            # Example success: {"success": true, ...}
            # Example error: {"error": "..."}
            if isinstance(resp_data, dict) and resp_data.get("error"):
                raise ValueError(f"Server Error: {resp_data['error']}")
        except json.JSONDecodeError:
            # Fallback if not JSON (legacy endpoints sometimes return HTML on error)
            pass

        return response.text
