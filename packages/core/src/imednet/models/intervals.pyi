"""Interval (visit definition) models for iMedNet."""

from __future__ import annotations

from datetime import datetime
from typing import Any, List, Optional

from pydantic import Field

from imednet.models.base import ImednetBaseModel
from imednet.models.engine import ModelEngine

class FormSummary(ImednetBaseModel):
    """Minimal form details embedded within an interval definition."""

    form_id: int = Field(0, alias="formId")
    form_key: str = Field("", alias="formKey")
    form_name: str = Field("", alias="formName")

    pass

class Interval(ImednetBaseModel):
    """Represents a visit interval or event within the study timeline."""

    forms: list[FormSummary] | None = Field(default=None, alias="forms")

    study_key: Optional[str]
    interval_id: Optional[int]
    interval_name: Optional[str]
    interval_description: Optional[str]
    interval_sequence: Optional[int]
    interval_group_id: Optional[int]
    interval_group_name: Optional[str]
    disabled: Optional[bool]
    date_created: Optional[str]
    date_modified: Optional[str]
    actual_date: Any
    actual_date_form: Any
    defined_using_interval: Any
    due_date_will_be_in: Any
    epro_grace_period: Any
    negative_slack: Any
    positive_slack: Any
    timeline: Any
    window_calculation_date: Any
    window_calculation_form: Any
