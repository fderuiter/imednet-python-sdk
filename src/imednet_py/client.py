from __future__ import annotations

import os
from typing import Any, Dict, Optional

import logging

import requests

from . import __version__


class ImednetAPIError(Exception):
    """Exception raised for API errors."""

    def __init__(self, status_code: int, code: Optional[str], description: str) -> None:
        self.status_code = status_code
        self.code = code
        self.description = description
        super().__init__(f"{status_code} {code or ''}: {description}")

API_BASE_URL = "https://edc.prod.imednetapi.com/api/v1/edc/"


class ImednetClient:
    """Simple client for the iMednet API."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        security_key: Optional[str] = None,
        *,
        base_url: str = API_BASE_URL,
    ) -> None:
        self.api_key = api_key or os.getenv("IMEDNET_API_KEY")
        self.security_key = security_key or os.getenv("IMEDNET_SECURITY_KEY")
        if not self.api_key or not self.security_key:
            raise ValueError("API and security keys are required")
        self.base_url = base_url
        self.session = self._build_session()

    # ------------------------------------------------------------------
    # session helpers

    def _build_session(self) -> requests.Session:
        """Create a requests session preloaded with authentication headers."""
        session = requests.Session()
        session.headers.update(
            {
                "x-api-key": self.api_key,
                "x-imn-security-key": self.security_key,
                "Accept": "application/json",
                "User-Agent": f"imednet-py/{__version__}",
            }
        )
        return session

    def _request(
        self,
        method: str,
        path: str,
        *,
        params: Optional[Dict[str, Any]] = None,
        json: Optional[Any] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: int | float = 30,
        retries: Any = None,
    ) -> Any:
        """Low-level HTTP helper used by the SDK."""

        url = self.base_url + path.lstrip("/")
        request_headers = self.session.headers.copy()
        if headers:
            request_headers.update(headers)

        response = self.session.request(
            method,
            url,
            params=params,
            json=json,
            headers=request_headers,
            timeout=timeout,
        )

        logging.debug(
            "HTTP %s %s -> %s in %.0f ms",
            method,
            url,
            response.status_code,
            response.elapsed.total_seconds() * 1000,
        )

        if 200 <= response.status_code < 300:
            if response.headers.get("Content-Type", "").startswith("application/json"):
                return response.json()
            return response.content

        try:
            payload = response.json()
        except ValueError:
            description = response.text
            code = None
        else:
            error_data = payload.get("metadata", {}).get("error", {})
            code = error_data.get("code")
            description = error_data.get("description", response.text)

        raise ImednetAPIError(response.status_code, code, description)
