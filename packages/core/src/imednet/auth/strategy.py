"""Authentication strategy protocol."""

from typing import Dict, List, Optional, Protocol, runtime_checkable


@runtime_checkable
class AuthStrategy(Protocol):
    """
    Protocol for authentication strategies.

    Strategies must provide headers to be injected into requests.
    """

    def get_headers(self) -> Dict[str, str]:
        """Return authentication headers."""
        ...

    def get_user_roles(self) -> List[str]:
        """Return resolved roles for the user, if available."""
        ...

    def get_user_id(self) -> Optional[str]:
        """Return user identity, if available."""
        ...
