from __future__ import annotations

from typing import Any, Dict, List

from pydantic import BaseModel, ConfigDict, Field


class Role(BaseModel):
    date_created: List[int] = Field(default_factory=list, alias="dateCreated")
    date_modified: List[int] = Field(default_factory=list, alias="dateModified")
    role_id: str = Field("", alias="roleId")
    community_id: int = Field(0, alias="communityId")
    name: str = Field("", alias="name")
    description: str = Field("", alias="description")
    level: int = Field(0, alias="level")
    type: str = Field("", alias="type")
    inactive: bool = Field(False, alias="inactive")

    # allow instantiation via field names or aliases
    model_config = ConfigDict(populate_by_name=True)

    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> Role:
        """
        Create a Role instance from JSON-like dict.
        """
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

    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> User:
        """
        Create a User instance from JSON-like dict, including nested Role parsing.
        """
        return cls.model_validate(data)
