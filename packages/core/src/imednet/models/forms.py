from __future__ import annotations

from imednet.models.engine import ModelEngine

from datetime import datetime

from pydantic import Field

from imednet.models.json_base import JsonModel


class Form(JsonModel):
    """Configuration and metadata for a CRF (Case Report Form)."""

Form = ModelEngine.get_model('Form', Form)

