"""Lightweight client for Veeva Vault metadata."""

from __future__ import annotations

from typing import Any, Dict, List

import requests
from pydantic import BaseModel, ConfigDict, Field, field_validator

from .models.validators import parse_bool, parse_list_or_default, parse_str_or_default


class VaultAuthError(Exception):
    """Raised when the Vault API returns 401."""


API_VER = "v24.3"


class VaultObject(BaseModel):
    """Minimal Vault object description."""

    name: str = Field("", alias="name__v")
    label: str = Field("", alias="label__v")

    model_config = ConfigDict(populate_by_name=True)

    @field_validator("name", "label", mode="before")
    def _fill_strs(cls, v: Any) -> str:
        return parse_str_or_default(v)


class VaultField(BaseModel):
    """Metadata about a single Vault field."""

    name: str = Field("", alias="name__v")
    label: str = Field("", alias="label__v")
    data_type: str = Field("", alias="data_type__v")
    required: bool = Field(False, alias="required__v")
    default_value: str | None = Field(None, alias="default_value__v")
    picklist_values: List[str] = Field(default_factory=list, alias="picklist_values__v")

    model_config = ConfigDict(populate_by_name=True)

    @field_validator("name", "label", "data_type", "default_value", mode="before")
    def _fill_strs(cls, v: Any) -> str | None:
        return parse_str_or_default(v) if v is not None else None

    @field_validator("required", mode="before")
    def _parse_bool(cls, v: Any) -> bool:
        return parse_bool(v)

    @field_validator("picklist_values", mode="before")
    def _parse_list(cls, v: Any) -> List[str]:
        return parse_list_or_default(v)

    @property
    def is_reference(self) -> bool:
        """Return True if this field is a lookup/reference."""

        return self.data_type == "Lookup"


class VaultClient:
    """Simple HTTP client for Vault metadata APIs."""

    def __init__(self, session_id: str, domain: str) -> None:
        self.session_id = session_id
        self.domain = domain.rstrip("/")

    def _headers(self) -> Dict[str, str]:
        return {"Authorization": self.session_id}

    def _url(self, path: str) -> str:
        return f"{self.domain}/api/{API_VER}{path}"

    def list_objects(self) -> List[VaultObject]:
        url = self._url("/metadata/vobjects")
        resp = requests.get(url, headers=self._headers())
        if resp.status_code == 401:
            raise VaultAuthError("Unauthorized")
        resp.raise_for_status()
        data = resp.json().get("data", [])
        return [VaultObject.model_validate(obj) for obj in data]

    def get_object_fields(self, object_api: str) -> List[VaultField]:
        url = self._url(f"/metadata/vobjects/{object_api}")
        resp = requests.get(url, headers=self._headers())
        if resp.status_code == 401:
            raise VaultAuthError("Unauthorized")
        resp.raise_for_status()
        data = resp.json().get("data", [])
        return [VaultField.model_validate(f) for f in data]


__all__ = [
    "VaultClient",
    "VaultObject",
    "VaultField",
    "VaultAuthError",
]
