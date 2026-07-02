"""Models for users and roles within iMedNet."""

from __future__ import annotations

from datetime import datetime
from typing import Any, List, Optional

from pydantic import Field, computed_field

from imednet.models.engine import ModelEngine
from imednet.models.json_base import JsonModel

class Role(JsonModel):
    """A role assigned to a user within a study or community."""

    role_id: str | None = Field(default=None, alias="roleId")
    name: str | None = Field(default=None, alias="name")
    description: str | None = Field(default=None, alias="description")
    level: int | None = Field(default=None, alias="level")
    type: str | None = Field(default=None, alias="type")
    inactive: bool | None = Field(default=None, alias="inactive")
    community_id: int | None = Field(default=None, alias="communityId")
    date_created: str | None = Field(default=None, alias="dateCreated")
    date_modified: str | None = Field(default=None, alias="dateModified")

class User(JsonModel):
    """A user account in the system."""

    @computed_field
    def name(self) -> str:
        """A convenience full-name property so you can do `user.name`.

        instead of f"{user.first_name} {user.last_name}" everywhere.
        """
        # will strip extra spaces if either is empty
        return " ".join(filter(None, (self.first_name, self.last_name)))

    user_id: Optional[str]
    login: Optional[str]
    first_name: Optional[str]
    last_name: Optional[str]
    email: Optional[str]
    user_active_in_study: Optional[bool]
    roles: Any
