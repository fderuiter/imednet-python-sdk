"""TODO: Add docstring."""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import Field

from imednet.models.engine import ModelEngine
from imednet.models.json_base import JsonModel


class Variable(JsonModel):
    """Definition of a data field (question) on a form."""

    label: str | None = Field(default=None, alias="label")
    variable_oid: str | None = Field(default=None, alias="variableOid")


Variable = ModelEngine.get_model('Variable', Variable)
