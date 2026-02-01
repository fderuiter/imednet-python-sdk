"""Authentication strategy protocol."""

from typing import Dict, Protocol


class AuthStrategy(Protocol):
    """
    Protocol for authentication strategies.

    Implementations must provide a method to retrieve authentication headers.
    """

    def get_headers(self) -> Dict[str, str]:
        """
        Return the headers required for authentication.

        Returns:
            A dictionary of header names and values.
        """
        ...
