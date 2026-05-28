from __future__ import annotations

from imednet.models.engine import ModelEngine

from datetime import datetime

from pydantic import Field

from imednet.models.json_base import JsonModel


class Coding(JsonModel):
    """Represents a medical coding entry associated with a record."""

Coding = ModelEngine.get_model('Coding', Coding)

