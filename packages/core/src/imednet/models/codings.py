from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import Field

from imednet.models.engine import ModelEngine
from imednet.models.json_base import JsonModel


class Coding(JsonModel):
    """Represents a medical coding entry associated with a record."""

    coding_id: Optional[str] = Field(None, alias="codingId")
    revision: Optional[int] = None
    reason: Optional[str] = None


Coding = ModelEngine.get_model('Coding', Coding)
