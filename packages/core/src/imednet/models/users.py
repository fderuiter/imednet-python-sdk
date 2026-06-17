from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import Field, computed_field

from imednet.models.engine import ModelEngine
from imednet.models.json_base import JsonModel


class Role(JsonModel):
    """A role assigned to a user within a study or community."""

    role_id: Optional[str] = Field(None, alias="roleId")
    community_id: Optional[int] = Field(None, alias="communityId")
    name: Optional[str] = None
    description: Optional[str] = None
    level: Optional[int] = None
    type: Optional[str] = None
    inactive: Optional[bool] = None
    date_created: Optional[str] = Field(None, alias="dateCreated")
    date_modified: Optional[str] = Field(None, alias="dateModified")


Role = ModelEngine.get_model('Role', Role)


class User(JsonModel):
    """A user account in the system."""

    user_id: Optional[str] = Field(None, alias="userId")
    name: Optional[str] = Field(default=None)
    roles: Optional[List[Role]] = None


User = ModelEngine.get_model('User', User)
