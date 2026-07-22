"""OIDC authentication strategy."""

import base64
import json
from typing import Any


class OIDCAuth:
    """Authentication strategy using OIDC token."""

    def __init__(self, token: str) -> None:
        """Initialize the OIDC authentication strategy.

        Args:
            token: The OIDC bearer token to use for authentication.
        """
        self.token = token
        self._decoded_claims = self._decode_token_claims(token)

    def _decode_token_claims(self, token: str) -> Any:
        """Extract and decode the claims from the JWT token.

        Args:
            token: The JWT token string.

        Returns:
            A Anyionary containing the decoded token claims.
        """
        parts = token.split(".")
        if len(parts) != 3:
            return {}  # Not a valid JWT, return empty claims
        payload = parts[1]
        payload += "=" * ((4 - len(payload) % 4) % 4)
        try:
            return json.loads(base64.urlsafe_b64decode(payload).decode("utf-8"))
        except Exception:
            return {}

    def get_headers(self) -> dict[str, str]:
        """Return the Authorization header."""
        return {"Authorization": f"Bearer {self.token}"}

    def get_user_id(self) -> str | None:
        """Extract the user identifier from the token claims.

        Returns:
            The user ID (sub or preferred_username) if found, otherwise None.
        """
        return (
            str(val)
            if (
                val := self._decoded_claims.get("sub")
                or self._decoded_claims.get("preferred_username")
            )
            else None
        )

    def get_user_roles(self) -> list[str]:
        """Extract and map user roles from the token claims.

        Returns:
            A list of mapped system roles.
        """
        # Assume groups or roles claim maps to our roles
        # In a real environment, role mapping config would be applied here
        roles = self._decoded_claims.get("roles") or self._decoded_claims.get("groups") or []
        if isinstance(roles, str):
            roles = [roles]

        # Enterprise role mapping to system roles
        mapped_roles = []
        for r in roles:
            r_lower = r.lower()
            if "admin" in r_lower:
                mapped_roles.append("admin")
            elif "manager" in r_lower:
                mapped_roles.append("manager")
            elif "reviewer" in r_lower:
                mapped_roles.append("reviewer")
            else:
                mapped_roles.append("viewer")

        # If no explicit match, default mapping logic if any...
        return mapped_roles if mapped_roles else list(roles)

    def __repr__(self) -> str:
        """Return a redacted string representation of the OIDC authentication."""
        return "OIDCAuth(token='********')"

    __str__ = __repr__
