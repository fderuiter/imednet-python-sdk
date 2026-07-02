"""Models for users and roles within iMedNet."""

from __future__ import annotations

from datetime import datetime
from typing import List

from pydantic import Field, computed_field

from imednet.models.engine import ModelEngine
from imednet.models.json_base import JsonModel



class Role(JsonModel):
    pass


class User(JsonModel):
    user_id: Optional[str]
    login: Optional[str]
    first_name: Optional[str]
    last_name: Optional[str]
    email: Optional[str]
    user_active_in_study: Optional[bool]
    roles: Any

