"""API Key authentication strategy."""

from dataclasses import dataclass
from typing import Dict

from imednet.constants import HEADER_API_KEY, HEADER_SECURITY_KEY
from imednet.auth.strategy import AuthStrategy


@dataclass
class ApiKeyAuth(AuthStrategy):
    """
    Authentication strategy using API Key and Security Key.
    """

    api_key: str
    security_key: str

    def get_headers(self) -> Dict[str, str]:
        """
        Return the headers required for API Key authentication.
        """
        return {
            HEADER_API_KEY: self.api_key,
            HEADER_SECURITY_KEY: self.security_key,
        }
