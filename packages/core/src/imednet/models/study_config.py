"""Study configuration models and validation.

This module provides Pydantic models for parsing and validating study configurations,
including reporting profiles, widgets, and mapping rules.
"""

from __future__ import annotations

from typing import Optional

from msgspec import field as Field

from imednet.models.json_base import JsonModel
from imednet.models.standards import PROFILE_REGISTRY


class MappingRule(JsonModel, kw_only=True, omit_defaults=True):
    """Mapping from raw source variable to canonical reporting field."""

    domain: str 
    target_field: str 
    source_form_key: str 
    source_variable_name: str 
    fallback_value: Optional[str] = Field(default=None)
    business_logic: Optional[str] = Field(default=None)
    is_baseline: bool = Field(default=False)


class WidgetConfig(JsonModel, kw_only=True, omit_defaults=True):
    """Declarative dashboard widget configuration."""

    widget_id: str 
    type: str 
    title: str 
    domain: str 
    x_axis: Optional[str] = Field(default=None)
    y_axis: Optional[str] = Field(default=None)
    layout_cols: int = Field(default=12)


class StudyConfiguration(JsonModel, kw_only=True, omit_defaults=True):
    """Serialized study reporting dashboard configuration."""

    version: str = Field(default="1.0.0")
    study_key: str 
    reporting_profile: str = Field(default="general")
    mappings: list[MappingRule] = Field(default_factory=list)
    terminology_lookups: dict[str, dict[str, str]] = Field(
        default_factory=dict, name="terminologyLookups"
    )
    widgets: list[WidgetConfig] = Field(default_factory=list)
    phi_fields: list[str] = Field(default_factory=list)
