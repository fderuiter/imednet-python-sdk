"""API Key authentication strategy."""

from typing import Dict

from imednet.constants import HEADER_API_KEY, HEADER_SECURITY_KEY


class ApiKeyAuth:
    """Authentication strategy using API Key and Security Key."""

    def __init__(self, api_key: str, security_key: str) -> None:
        self.api_key = api_key
        self.security_key = security_key

    def get_headers(self) -> Dict[str, str]:
        """Return the API key and security key headers."""
        return {
            HEADER_API_KEY: self.api_key,
            HEADER_SECURITY_KEY: self.security_key,
        }
