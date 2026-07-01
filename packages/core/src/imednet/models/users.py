"""Models for users and roles within iMedNet."""

from __future__ import annotations

from datetime import datetime
from typing import List

from msgspec import field as Field

from imednet.models.engine import ModelEngine
from imednet.models.json_base import JsonModel


class Role(JsonModel, kw_only=True, omit_defaults=True):
    """A role assigned to a user within a study or community."""

    role_id: str | None = Field(default=None)
    name: str | None = Field(default=None)
    description: str | None = Field(default=None)
    level: int | None = Field(default=None)
    type: str | None = Field(default=None)
    inactive: bool | None = Field(default=None)
    community_id: int | None = Field(default=None)
    date_created: str | None = Field(default=None)
    date_modified: str | None = Field(default=None)


Role = ModelEngine.get_model('Role', Role)


class User(JsonModel, kw_only=True, omit_defaults=True):
    """A user account in the system."""

    @property
    def name(self) -> str:
        """A convenience full-name property so you can do `user.name`.

        instead of f"{user.first_name} {user.last_name}" everywhere.
        """
        # will strip extra spaces if either is empty
        return " ".join(filter(None, (self.first_name, self.last_name)))


User = ModelEngine.get_model('User', User)
