"""Authentication strategy protocol."""

from typing import Dict, Protocol, runtime_checkable


@runtime_checkable
class AuthStrategy(Protocol):
    """
    Protocol for authentication strategies.

    Strategies must provide headers to be injected into requests.
    """

    def get_headers(self) -> Dict[str, str]:
        """Return authentication headers."""
        ...
