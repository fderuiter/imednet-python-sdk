from __future__ import annotations

from imednet.models.engine import ModelEngine

from datetime import datetime
from typing import Optional

from pydantic import Field

from imednet.models.json_base import JsonModel


class Variable(JsonModel):
    """Definition of a data field (question) on a form."""


    pass
Variable = ModelEngine.get_model('Variable', Variable)

