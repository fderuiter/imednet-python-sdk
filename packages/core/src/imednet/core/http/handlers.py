"""
HTTP response handling and error mapping.
"""

from __future__ import annotations

import json

import httpx

from imednet.errors import get_error_class


def handle_response(response: httpx.Response) -> httpx.Response:
    """Return the response or raise an appropriate ``ApiError``."""
    if response.is_error:
        status = response.status_code
        try:
            body = response.json()
        except json.JSONDecodeError:
            body = response.text

        exc_cls = get_error_class(status)
        raise exc_cls(body, status_code=status)
    return response
