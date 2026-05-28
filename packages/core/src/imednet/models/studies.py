from __future__ import annotations

from imednet.models.engine import ModelEngine

from datetime import datetime

from pydantic import Field

from imednet.models.json_base import JsonModel


class Study(JsonModel):
    """Represents a clinical study and its metadata."""

Study = ModelEngine.get_model('Study', Study)

