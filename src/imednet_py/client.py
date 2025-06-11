from __future__ import annotations

API_BASE_URL = "https://edc.prod.imednetapi.com/api/v1/edc/"

import httpx


class ImednetClient:
    """Simple client for the iMednet API."""

    def __init__(self, api_key: str, security_key: str) -> None:
        self.api_key = api_key
        self.security_key = security_key
        self.session = self._build_session()

    def _build_session(self) -> httpx.Client:
        """Create an HTTPX client preloaded with authentication headers."""
        return httpx.Client(
            base_url=API_BASE_URL,
            headers={
                "x-api-key": self.api_key,
                "x-imn-security-key": self.security_key,
            },
        )
