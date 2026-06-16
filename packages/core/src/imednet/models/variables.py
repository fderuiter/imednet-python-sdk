from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import Field

from imednet.models.engine import ModelEngine
from imednet.models.json_base import JsonModel


class Variable(JsonModel):
    """Definition of a data field (question) on a form."""

    label: Optional[str] = None

Variable = ModelEngine.get_model('Variable', Variable)
