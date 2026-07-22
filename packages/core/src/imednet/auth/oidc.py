"""OIDC authentication strategy."""

import base64
import json
from typing import Any


class OIDCAuth:
    """Authentication strategy using OIDC token."""

    def __init__(self, token: str) -> None:
        self.token = token

    def extract_user_info(self) -> dict[str, Any]:
        """Extract user information from the token."""
        try:
            parts = self.token.split(".")
            if len(parts) != 3:
                raise ValueError("Invalid JWT format")

            payload = parts[1]
            padded = payload + "=" * (-len(payload) % 4)
            decoded = base64.b64decode(padded).decode("utf-8")
            return json.loads(decoded)
        except Exception as e:
            raise ValueError(f"Failed to parse OIDC token: {e}") from e
