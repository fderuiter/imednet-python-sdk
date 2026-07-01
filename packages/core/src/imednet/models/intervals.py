"""Interval (visit definition) models for iMedNet."""

from __future__ import annotations

from datetime import datetime
from typing import List

from msgspec import field as Field

from imednet.models.engine import ModelEngine
from imednet.models.json_base import JsonModel


class FormSummary(JsonModel, kw_only=True, omit_defaults=True):
    """Minimal form details embedded within an interval definition."""

    form_id: int = Field(default=0)
    form_key: str = Field(default="")
    form_name: str = Field(default="")

    pass


class Interval(JsonModel, kw_only=True, omit_defaults=True):
    """Represents a visit interval or event within the study timeline."""

    forms: list[FormSummary] | None = Field(default=None)


Interval = ModelEngine.get_model('Interval', Interval)
