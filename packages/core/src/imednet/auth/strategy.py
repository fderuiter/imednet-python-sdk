"""Authentication strategy protocol."""

from typing import Dict, List, Optional, Protocol, runtime_checkable  # noqa: UP035


@runtime_checkable
class AuthStrategy(Protocol):
    """Protocol for authentication strategies.

    Strategies must provide headers to be injected into requests.
    """

    def get_headers(self) -> dict[str, str]:
        """Return authentication headers."""
        ...

    def get_user_roles(self) -> list[str]:
        """Return resolved roles for the user, if available."""
        ...

    def get_user_id(self) -> str | None:
        """Return user identity, if available."""
        ...
