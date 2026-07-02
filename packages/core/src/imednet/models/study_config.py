"""Study configuration models and validation.

This module provides Pydantic models for parsing and validating study configurations,
including reporting profiles, widgets, and mapping rules.
"""

from __future__ import annotations

from typing import Optional

from pydantic import Field, field_validator

from imednet.models.base import ImednetBaseModel
from imednet.models.standards import PROFILE_REGISTRY


class MappingRule(ImednetBaseModel):
    """Mapping from raw source variable to canonical reporting field."""

    domain: str = Field(..., alias="domain")
    target_field: str = Field(..., alias="targetField")
    source_form_key: str = Field(..., alias="sourceFormKey")
    source_variable_name: str = Field(..., alias="sourceVariableName")
    fallback_value: Optional[str] = Field(None, alias="fallbackValue")
    business_logic: Optional[str] = Field(None, alias="businessLogic")
    is_baseline: bool = Field(False, alias="isBaseline")


class WidgetConfig(ImednetBaseModel):
    """Declarative dashboard widget configuration."""

    widget_id: str = Field(..., alias="widgetId")
    type: str = Field(..., alias="type")
    title: str = Field(..., alias="title")
    domain: str = Field(..., alias="domain")
    x_axis: Optional[str] = Field(None, alias="xAxis")
    y_axis: Optional[str] = Field(None, alias="yAxis")
    layout_cols: int = Field(12, alias="layoutCols")


class StudyConfiguration(ImednetBaseModel):
    """Serialized study reporting dashboard configuration."""

    version: str = Field("1.0.0", alias="version")
    study_key: str = Field(..., alias="studyKey")
    reporting_profile: str = Field("general", alias="reportingProfile")
    mappings: list[MappingRule] = Field(default_factory=list, alias="mappings")
    terminology_lookups: dict[str, dict[str, str]] = Field(
        default_factory=dict, alias="terminologyLookups"
    )
    widgets: list[WidgetConfig] = Field(default_factory=list, alias="widgets")
    phi_fields: list[str] = Field(default_factory=list, alias="phiFields")

    @field_validator("reporting_profile", check_fields=False, mode="before")
    @classmethod
    def _validate_reporting_profile(cls, value: object) -> object:
        """Ensure the reporting profile exists in the registry."""
        if not isinstance(value, str):
            raise ValueError("reportingProfile must be a string.")

        profile_name = value.strip().lower()
        if profile_name in PROFILE_REGISTRY.list_profiles():
            return profile_name

        available_profiles = ", ".join(PROFILE_REGISTRY.list_profiles())
        raise ValueError(f"reportingProfile must be one of: {available_profiles}")
