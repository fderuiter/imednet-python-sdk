from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Optional

__all__ = ["Config", "load_config"]


@dataclass(frozen=True)
class Config:
    api_key: str
    security_key: str
    base_url: Optional[str] = None


def load_config(
    api_key: Optional[str] = None,
    security_key: Optional[str] = None,
    base_url: Optional[str] = None,
) -> Config:
    """Return configuration using arguments or environment variables."""
    api_key = api_key if api_key is not None else os.getenv("IMEDNET_API_KEY")
    security_key = security_key if security_key is not None else os.getenv("IMEDNET_SECURITY_KEY")
    base_url = base_url if base_url is not None else os.getenv("IMEDNET_BASE_URL")

    api_key = (api_key or "").strip()
    security_key = (security_key or "").strip()
    base_url = base_url.strip() if base_url else None

    if not api_key or not security_key:
        raise ValueError("API key and security key are required")

    return Config(api_key=api_key, security_key=security_key, base_url=base_url)
