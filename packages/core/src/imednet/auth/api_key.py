"""API Key authentication strategy."""

from typing import Dict

from imednet.constants import HEADER_API_KEY, HEADER_SECURITY_KEY


class ApiKeyAuth:
    """Authentication strategy using API Key and Security Key."""

    def __init__(self, api_key: str, security_key: str) -> None:
        """TODO: Add docstring."""
        self.api_key = api_key
        self.security_key = security_key

    def get_headers(self) -> Dict[str, str]:
        """Return the API key and security key headers."""
        return {
            HEADER_API_KEY: self.api_key,
            HEADER_SECURITY_KEY: self.security_key,
        }

    def get_user_roles(self) -> list[str]:
        """TODO: Add docstring."""
        # Server-side role resolution for API keys would require an API call.
        # For legacy fallback, this could be handled at the endpoint level,
        # but here we return empty or "admin" if we trust the key.
        # We will let the API handle authorization.
        return []

    def get_user_id(self) -> str | None:
        """TODO: Add docstring."""
        return "api-key-user"

    def __repr__(self) -> str:
        """TODO: Add docstring."""
        return "ApiKeyAuth(api_key='********', security_key='********')"

    __str__ = __repr__
