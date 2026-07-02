"""Models for form variables (data fields) in iMedNet."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import Field

from imednet.models.engine import ModelEngine
from imednet.models.json_base import JsonModel

class Variable(JsonModel):
    """Definition of a data field (question) on a form."""

    study_key: Optional[str]
    variable_id: Optional[int]
    variable_type: Optional[str]
    variable_name: Optional[str]
    sequence: Optional[int]
    revision: Optional[int]
    date_created: Optional[str]
    date_modified: Optional[str]
    form_id: Optional[int]
    form_key: Optional[str]
    form_name: Optional[str]
    blinded: Any
    deleted: Any
    disabled: Any

    label: str | None = Field(default=None, alias="label")
    variable_oid: str | None = Field(default=None, alias="variableOid")
