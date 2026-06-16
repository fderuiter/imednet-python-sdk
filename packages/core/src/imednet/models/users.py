from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import Field, computed_field

from imednet.models.engine import ModelEngine
from imednet.models.json_base import JsonModel


class Role(JsonModel):
    """A role assigned to a user within a study or community."""


Role = ModelEngine.get_model('Role', Role)


class User(JsonModel):
    """A user account in the system."""
    
    name: Optional[str] = Field(default=None)

User = ModelEngine.get_model('User', User)
