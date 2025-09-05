from __future__ import annotations

from datetime import datetime
from typing import List

from pydantic import Field, computed_field

from .json_base import JsonModel


class Role(JsonModel):
    """Represents a user role within a study or site."""

    date_created: datetime = Field(
        default_factory=datetime.now,
        alias="dateCreated",
        description="The date the role was created.",
    )
    date_modified: datetime = Field(
        default_factory=datetime.now,
        alias="dateModified",
        description="The date the role was last modified.",
    )
    role_id: str = Field("", alias="roleId", description="The ID of the role.")
    community_id: int = Field(0, alias="communityId", description="The ID of the community.")
    name: str = Field("", alias="name", description="The name of the role.")
    description: str = Field("", alias="description", description="The description of the role.")
    level: int = Field(0, alias="level", description="The level of the role.")
    type: str = Field("", alias="type", description="The type of the role.")
    inactive: bool = Field(
        False, alias="inactive", description="Indicates if the role is inactive."
    )


class User(JsonModel):
    """Represents a user in the system."""

    user_id: str = Field("", alias="userId", description="The ID of the user.")
    login: str = Field("", alias="login", description="The login name of the user.")
    first_name: str = Field("", alias="firstName", description="The first name of the user.")
    last_name: str = Field("", alias="lastName", description="The last name of the user.")
    email: str = Field("", alias="email", description="The email address of the user.")
    user_active_in_study: bool = Field(
        False,
        alias="userActiveInStudy",
        description="Indicates if the user is active in the study.",
    )
    roles: List[Role] = Field(
        default_factory=list, alias="roles", description="A list of roles assigned to the user."
    )

    @computed_field
    def name(self) -> str:
        """
        A convenience full-name property so you can do `user.name`
        instead of f"{user.first_name} {user.last_name}" everywhere.
        """
        # will strip extra spaces if either is empty
        return " ".join(filter(None, (self.first_name, self.last_name)))
