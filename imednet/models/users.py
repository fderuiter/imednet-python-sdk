from __future__ import annotations

from datetime import datetime
from typing import List

from pydantic import Field, computed_field

from imednet.models.json_base import JsonModel


class Role(JsonModel):
    date_created: datetime = Field(default_factory=datetime.now, alias="dateCreated")
    date_modified: datetime = Field(default_factory=datetime.now, alias="dateModified")
    role_id: str = Field("", alias="roleId")
    community_id: int = Field(0, alias="communityId")
    name: str = Field("", alias="name")
    description: str = Field("", alias="description")
    level: int = Field(0, alias="level")
    type: str = Field("", alias="type")
    inactive: bool = Field(False, alias="inactive")

    pass


class User(JsonModel):
    user_id: str = Field("", alias="userId")
    login: str = Field("", alias="login")
    first_name: str = Field("", alias="firstName")
    last_name: str = Field("", alias="lastName")
    email: str = Field("", alias="email")
    user_active_in_study: bool = Field(False, alias="userActiveInStudy")
    roles: List[Role] = Field(default_factory=list, alias="roles")

    pass

    @computed_field
    def name(self) -> str:
        """
        A convenience full-name property so you can do `user.name`
        instead of f"{user.first_name} {user.last_name}" everywhere.
        """
        # will strip extra spaces if either is empty
        return " ".join(filter(None, (self.first_name, self.last_name)))
