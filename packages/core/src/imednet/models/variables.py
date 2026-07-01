"""Models for form variables (data fields) in iMedNet."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from msgspec import field as Field

from imednet.models.engine import ModelEngine
from imednet.models.json_base import JsonModel


class Variable(JsonModel, kw_only=True, omit_defaults=True):
    """Definition of a data field (question) on a form."""

    label: str | None = Field(default=None)
    variable_oid: str | None = Field(default=None)


Variable = ModelEngine.get_model('Variable', Variable)
