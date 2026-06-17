from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import Field

from imednet.models.engine import ModelEngine
from imednet.models.json_base import JsonModel


class Variable(JsonModel):
    """Definition of a data field (question) on a form."""

    label: Optional[str] = None
    variable_id: Optional[str] = Field(None, alias="variableId")
    variable_name: Optional[str] = Field(None, alias="variableName")
    variable_type: Optional[str] = Field(None, alias="variableType")
    disabled: Optional[bool] = None
    variable_oid: Optional[str] = Field(None, alias="variableOid")
    deleted: Optional[bool] = None
    blinded: Optional[bool] = None


Variable = ModelEngine.get_model('Variable', Variable)
