"""API Key authentication strategy."""

from imednet.constants import HEADER_API_KEY, HEADER_SECURITY_KEY


class ApiKeyAuth:
    """Authentication strategy using API Key and Security Key."""

    def __init__(self, api_key: str, security_key: str) -> None:
        """Initialize the API Key authentication strategy.

        Args:
            api_key: The iMednet API key.
            security_key: The iMednet security key.
        """
        self.api_key = api_key
        self.security_key = security_key

    def get_headers(self) -> dict[str, str]:
        """Return the API key and security key headers."""
        return {
            HEADER_API_KEY: self.api_key,
            HEADER_SECURITY_KEY: self.security_key,
        }

    def get_user_roles(self) -> list[str]:
        """Return the roles associated with the authenticated user.

        Returns:
            list[str]: An empty list, as roles are handled by the API.
        """
        # Server-side role resolution for API keys would require an API call.
        # For legacy fallback, this could be handled at the endpoint level,
        # but here we return empty or "admin" if we trust the key.
        # We will let the API handle authorization.
        return []

    def get_user_id(self) -> str | None:
        """Return the ID of the authenticated user.

        Returns:
            str | None: A placeholder user ID for API key users.
        """
        return "api-key-user"

    def __repr__(self) -> str:
        """Return a redacted string representation of the authentication object.

        Returns:
            str: The redacted string.
        """
        return "ApiKeyAuth(api_key='********', security_key='********')"

    __str__ = __repr__
