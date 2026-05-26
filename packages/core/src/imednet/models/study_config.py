from __future__ import annotations

from typing import Optional

from pydantic import Field

from imednet.models.json_base import JsonModel


class MappingRule(JsonModel):
    """Mapping from raw source variable to canonical reporting field."""

    domain: str = Field(..., alias="domain")
    target_field: str = Field(..., alias="targetField")
    source_form_key: str = Field(..., alias="sourceFormKey")
    source_variable_name: str = Field(..., alias="sourceVariableName")
    fallback_value: Optional[str] = Field(None, alias="fallbackValue")


class WidgetConfig(JsonModel):
    """Declarative dashboard widget configuration."""

    widget_id: str = Field(..., alias="widgetId")
    type: str = Field(..., alias="type")
    title: str = Field(..., alias="title")
    domain: str = Field(..., alias="domain")
    x_axis: Optional[str] = Field(None, alias="xAxis")
    y_axis: Optional[str] = Field(None, alias="yAxis")
    layout_cols: int = Field(12, alias="layoutCols")


class StudyConfiguration(JsonModel):
    """Serialized study reporting dashboard configuration."""

    version: str = Field("1.0.0", alias="version")
    study_key: str = Field(..., alias="studyKey")
    reporting_profile: str = Field("general", alias="reportingProfile")
    mappings: list[MappingRule] = Field(default_factory=list, alias="mappings")
    terminology_lookups: dict[str, dict[str, str]] = Field(
        default_factory=dict, alias="terminologyLookups"
    )
    widgets: list[WidgetConfig] = Field(default_factory=list, alias="widgets")
