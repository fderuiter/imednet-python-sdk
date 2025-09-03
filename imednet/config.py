from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Optional

__all__ = ["Config", "load_config_from_env"]


@dataclass(frozen=True)
class Config:
    """A container for the SDK's configuration settings.

    Attributes:
        api_key: The API key for authentication.
        security_key: The security key for authentication.
        base_url: The base URL of the iMednet API.
    """

    api_key: str
    security_key: str
    base_url: Optional[str] = None


def load_config_from_env(
    api_key: Optional[str] = None,
    security_key: Optional[str] = None,
    base_url: Optional[str] = None,
) -> Config:
    """Load configuration from arguments or fall back to environment variables.

    Args:
        api_key: The API key. If not provided, `IMEDNET_API_KEY` is used.
        security_key: The security key. If not provided, `IMEDNET_SECURITY_KEY` is used.
        base_url: The base URL. If not provided, `IMEDNET_BASE_URL` is used.

    Returns:
        A `Config` object with the loaded settings.

    Raises:
        ValueError: If the API key or security key is not provided.
    """
    api_key = api_key if api_key is not None else os.getenv("IMEDNET_API_KEY")
    security_key = security_key if security_key is not None else os.getenv("IMEDNET_SECURITY_KEY")
    base_url = base_url if base_url is not None else os.getenv("IMEDNET_BASE_URL")

    api_key = (api_key or "").strip()
    security_key = (security_key or "").strip()
    base_url = base_url.strip() if base_url else None

    if not api_key and not security_key:
        raise ValueError("API key and security key are required")
    if not api_key:
        raise ValueError("API key is required")
    if not security_key:
        raise ValueError("Security key is required")

    return Config(api_key=api_key, security_key=security_key, base_url=base_url)
