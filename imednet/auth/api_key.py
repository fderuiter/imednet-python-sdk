"""
API Key authentication strategy.
"""

from typing import Dict

from imednet.auth.strategy import AuthStrategy
from imednet.constants import HEADER_API_KEY, HEADER_SECURITY_KEY


class ApiKeyAuth(AuthStrategy):
    """
    Authentication strategy using API Key and Security Key.

    This is the standard authentication method for iMedNet API.
    """

    def __init__(self, api_key: str, security_key: str) -> None:
        """
        Initialize with API credentials.

        Args:
            api_key: The iMedNet API Key.
            security_key: The iMedNet Security Key.
        """
        self.api_key = api_key
        self.security_key = security_key

    def get_headers(self) -> Dict[str, str]:
        """
        Return the API Key and Security Key headers.

        Returns:
            Dictionary containing x-api-key and x-imn-security-key.
        """
        return {
            HEADER_API_KEY: self.api_key,
            HEADER_SECURITY_KEY: self.security_key,
        }
