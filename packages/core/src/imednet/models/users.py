"""TODO: Add docstring."""

from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import Field, computed_field

from imednet.models.json_base import JsonModel


class Role(JsonModel):
    """TODO: Add docstring."""

    role_id: Optional[str] = Field(default=None, alias="roleId")
    name: Optional[str] = Field(default=None, alias="name")
    description: Optional[str] = Field(default=None, alias="description")
    level: Optional[int] = Field(default=None, alias="level")
    type: Optional[str] = Field(default=None, alias="type")
    inactive: Optional[bool] = Field(default=None, alias="inactive")
    community_id: Optional[int] = Field(default=None, alias="communityId")
    date_created: Optional[str] = Field(default=None, alias="dateCreated")
    date_modified: Optional[str] = Field(default=None, alias="dateModified")



class User(JsonModel):
    """TODO: Add docstring."""

    user_id: Optional[str] = Field(default=None, alias="userId")
    login: Optional[str] = Field(default=None, alias="login")
    first_name: Optional[str] = Field(default=None, alias="firstName")
    last_name: Optional[str] = Field(default=None, alias="lastName")
    email: Optional[str] = Field(default=None, alias="email")
    user_active_in_study: Optional[bool] = Field(default=None, alias="userActiveInStudy")

    @computed_field
    def name(self) -> str:
        """A convenience full-name property so you can do `user.name`.

        instead of f"{user.first_name} {user.last_name}" everywhere.
        """
        # will strip extra spaces if either is empty
        return " ".join(filter(None, (self.first_name, self.last_name)))
