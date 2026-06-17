from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import Field

from imednet.models.engine import ModelEngine
from imednet.models.json_base import JsonModel


class Study(JsonModel):
    """Represents a clinical study and its metadata."""

    study_key: Optional[str] = Field(None, alias="studyKey")


Study = ModelEngine.get_model('Study', Study)
