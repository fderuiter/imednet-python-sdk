from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List

from pydantic import BaseModel, ConfigDict, Field, computed_field, field_validator

from imednet.utils.validators import (
    parse_bool,
    parse_datetime,
    parse_int_or_default,
    parse_list_or_default,
    parse_str_or_default,
)


class Role(BaseModel):
    date_created: datetime = Field(default_factory=datetime.now, alias="dateCreated")
    date_modified: datetime = Field(default_factory=datetime.now, alias="dateModified")
    role_id: str = Field("", alias="roleId")
    community_id: int = Field(0, alias="communityId")
    name: str = Field("", alias="name")
    description: str = Field("", alias="description")
    level: int = Field(0, alias="level")
    type: str = Field("", alias="type")
    inactive: bool = Field(False, alias="inactive")

    model_config = ConfigDict(populate_by_name=True)

    # —— Parse or default datetimes
    @field_validator("date_created", "date_modified", mode="before")
    def _parse_datetimes(cls, v):
        return parse_datetime(v)

    @field_validator("community_id", "level", mode="before")
    def _fill_ints(cls, v):
        return parse_int_or_default(v)

    @field_validator("role_id", "name", "description", "type", mode="before")
    def _fill_strs(cls, v):
        return parse_str_or_default(v)

    @field_validator("inactive", mode="before")
    def parse_bool_field(cls, v):
        return parse_bool(v)

    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> Role:
        """Create a Role from JSON-like dict."""
        return cls.model_validate(data)


class User(BaseModel):
    user_id: str = Field("", alias="userId")
    login: str = Field("", alias="login")
    first_name: str = Field("", alias="firstName")
    last_name: str = Field("", alias="lastName")
    email: str = Field("", alias="email")
    user_active_in_study: bool = Field(False, alias="userActiveInStudy")
    roles: List[Role] = Field(default_factory=list, alias="roles")

    model_config = ConfigDict(populate_by_name=True)

    # —— Coerce None → default strings
    @field_validator("user_id", "login", "first_name", "last_name", "email", mode="before")
    def _fill_strs(cls, v):
        return parse_str_or_default(v)

    # —— Coerce None → default bool
    @field_validator("user_active_in_study", mode="before")
    def _parse_active_flag(cls, v):
        return parse_bool(v)

    # —— Coerce None → empty list for roles
    @field_validator("roles", mode="before")
    def _fill_roles(cls, v):
        return parse_list_or_default(v)

    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> User:
        """Create a User from JSON-like dict, with nested Role parsing."""
        return cls.model_validate(data)

    @computed_field
    def name(self) -> str:
        """
        A convenience full-name property so you can do `user.name`
        instead of f"{user.first_name} {user.last_name}" everywhere.
        """
        # will strip extra spaces if either is empty
        return " ".join(filter(None, (self.first_name, self.last_name)))
