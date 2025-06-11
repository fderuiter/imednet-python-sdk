from __future__ import annotations

import os
from typing import Optional

import requests

from . import __version__

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
