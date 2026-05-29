from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Optional

__all__ = ["Config", "load_config"]


@dataclass(frozen=True)
class Config:
    api_key: Optional[str] = None
    security_key: Optional[str] = None
    base_url: Optional[str] = None
    oidc_token: Optional[str] = None

    def __repr__(self) -> str:
        return f"Config(api_key='********', security_key='********', oidc_token='********', base_url={self.base_url!r})"


def load_config(
    api_key: Optional[str] = None,
    security_key: Optional[str] = None,
    base_url: Optional[str] = None,
    oidc_token: Optional[str] = None,
) -> Config:
    """Return configuration using arguments or environment variables."""
    api_key = api_key if api_key is not None else os.getenv("IMEDNET_API_KEY")
    security_key = security_key if security_key is not None else os.getenv("IMEDNET_SECURITY_KEY")
    base_url = base_url if base_url is not None else os.getenv("IMEDNET_BASE_URL")
    oidc_token = oidc_token if oidc_token is not None else os.getenv("IMEDNET_OIDC_TOKEN")

    api_key = (api_key or "").strip() or None
    security_key = (security_key or "").strip() or None
    base_url = base_url.strip() if base_url else None
    oidc_token = (oidc_token or "").strip() or None

    if not oidc_token:
        if not api_key and not security_key:
            raise ValueError("Either OIDC token or both API key and security key are required")
        if not api_key:
            raise ValueError("API key is required when not using OIDC")
        if not security_key:
            raise ValueError("Security key is required when not using OIDC")

    return Config(
        api_key=api_key, security_key=security_key, base_url=base_url, oidc_token=oidc_token
    )
