"""
Authentication strategy protocol.
"""

from typing import Dict, Protocol


class AuthStrategy(Protocol):
    """
    Protocol for authentication strategies.

    Classes implementing this protocol define how to inject authentication
    credentials into HTTP requests.
    """

    def get_headers(self) -> Dict[str, str]:
        """
        Return headers required for authentication.

        Returns:
            A dictionary of header names and values.
        """
        ...
