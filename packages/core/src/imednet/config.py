"""Global SDK configuration state.

This module provides the core configuration object for the iMednet SDK.
"""

from __future__ import annotations

import os
from typing import Optional

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

__all__ = ["Config", "load_config"]


class Config(BaseSettings):
    """Configuration object for the SDK client."""

    model_config = SettingsConfigDict(
        env_prefix="IMEDNET_",
        env_file=".env",
        extra="ignore",
    )

    # Core
    api_key: Optional[str] = Field(
        default=None,
        description="API key used for authentication.",
        json_schema_extra={"category": "Core"},
    )
    security_key: Optional[str] = Field(
        default=None,
        description="Security key used for authentication.",
        json_schema_extra={"category": "Core"},
    )
    base_url: Optional[str] = Field(
        default=None,
        description="Optional base URL for private deployments.",
        json_schema_extra={"category": "Core"},
    )
    oidc_token: Optional[str] = Field(
        default=None,
        description="Optional OIDC token for authentication.",
        json_schema_extra={"category": "Core"},
    )
    timeout: float = Field(
        default=30.0,
        description="API request timeout in seconds.",
        json_schema_extra={"category": "Core"},
    )
    high_contrast: bool = Field(
        default=False,
        description="Enable high contrast mode for the CLI.",
        json_schema_extra={"category": "Core"},
    )

    # Test
    study_key: Optional[str] = Field(
        default=None,
        description="Study identifier used by examples and some tests.",
        json_schema_extra={"category": "Test"},
    )
    run_e2e: bool = Field(
        default=False,
        description="Set to ``1`` to enable end-to-end tests that hit a live environment.",
        json_schema_extra={"category": "Test"},
    )
    batch_id: Optional[str] = Field(
        default=None,
        description="Batch identifier used by job polling tests. Created automatically if unset.",
        json_schema_extra={"category": "Test"},
    )
    form_key: Optional[str] = Field(
        default=None,
        description="Form key for record-creation tests. If unset, the first form is used.",
        json_schema_extra={"category": "Test"},
    )
    allow_mutation: bool = Field(
        default=False,
        description="Set to ``1`` to allow workflow tests that submit data.",
        json_schema_extra={"category": "Test"},
    )
    postman_path: Optional[str] = Field(
        default=None,
        description="Path to postman collection for drift testing.",
        json_schema_extra={"category": "Test"},
    )
    strict_mode: bool = Field(
        default=False,
        description="Enable strict mode for schema validation in tests.",
        json_schema_extra={"category": "Test"},
    )
    test_containers: bool = Field(
        default=False,
        description="Set to ``1`` to run integration tests that require Docker containers.",
        json_schema_extra={"category": "Test"},
    )

    # Plugins
    tenant_db_path: str = Field(
        default=os.path.expanduser("~/.imednet/enterprise_portal.sqlite3"),
        description="Path to the SQLite database for Enterprise Portal plugin.",
        json_schema_extra={"category": "Plugins"},
    )
    triage_db_path: Optional[str] = Field(
        default=None,
        description="Path to the SQLite database for Review Workbench plugin triage.",
        json_schema_extra={"category": "Plugins"},
    )
    config_db_path: str = Field(
        default=str(os.path.expanduser("~/.imednet/config_versions.sqlite3")),
        description="Path to the SQLite database for workflow version control.",
        json_schema_extra={"category": "Plugins"},
    )

    @model_validator(mode="after")
    def validate_auth(self) -> Config:  # noqa: N804
        """Validate that required authentication parameters are provided."""
        ak = (self.api_key or "").strip() or None
        sk = (self.security_key or "").strip() or None
        ot = (self.oidc_token or "").strip() or None

        self.api_key = ak
        self.security_key = sk
        self.oidc_token = ot
        self.base_url = self.base_url.strip() if self.base_url else None

        if not ot:
            if not ak and not sk:
                raise ValueError("Either OIDC token or both API key and security key are required")
            if not ak:
                raise ValueError("API key is required when not using OIDC")
            if not sk:
                raise ValueError("Security key is required when not using OIDC")
        return self

    def __repr__(self) -> str:
        """Return a string representation of the configuration.

        Security-sensitive fields are masked.

        Returns:
            A string representation of the configuration.
        """
        return f"Config(api_key='********', security_key='********', oidc_token='********', base_url={self.base_url!r})"


# Ensure that all fields have descriptions
for field_name, field_info in Config.model_fields.items():
    if not field_info.description:
        raise ValueError(
            f"Configuration variable '{field_name}' must have a mandatory description string."
        )


def load_config(
    api_key: Optional[str] = None,
    security_key: Optional[str] = None,
    base_url: Optional[str] = None,
    oidc_token: Optional[str] = None,
) -> Config:
    """Return configuration using arguments or environment variables.

    Args:
        api_key: The API key for authentication. Defaults to IMEDNET_API_KEY environment variable.
        security_key: The security key for authentication. Defaults to IMEDNET_SECURITY_KEY environment variable.
        base_url: The base URL for the iMednet API. Defaults to IMEDNET_BASE_URL environment variable.
        oidc_token: Optional OIDC token. Defaults to IMEDNET_OIDC_TOKEN environment variable.

    Returns:
        The loaded SDK configuration.

    Raises:
        ValueError: If required authentication parameters are missing.
    """
    kwargs = {}
    if api_key is not None:
        kwargs["api_key"] = api_key
    if security_key is not None:
        kwargs["security_key"] = security_key
    if base_url is not None:
        kwargs["base_url"] = base_url
    if oidc_token is not None:
        kwargs["oidc_token"] = oidc_token

    return Config(**kwargs)
