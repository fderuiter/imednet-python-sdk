"""Simple client and mapping helpers for Veeva Vault API."""

from __future__ import annotations

from typing import Any, Dict, Iterable, List, Mapping, MutableMapping, Tuple

import httpx


class VeevaVaultClient:
    """HTTP client wrapper for interacting with the Veeva Vault API."""

    DEFAULT_BASE_URL = "https://{vault}.veevavault.com"

    def __init__(
        self,
        vault: str,
        client_id: str,
        client_secret: str,
        username: str,
        password: str,
        base_url: str | None = None,
        api_version: str = "v21.3",
    ) -> None:
        self.vault = vault
        self.client_id = client_id
        self.client_secret = client_secret
        self.username = username
        self.password = password
        self.base_url = base_url or self.DEFAULT_BASE_URL.format(vault=vault)
        self.api_version = api_version
        self._access_token: str | None = None
        self._client = httpx.Client(base_url=self.base_url)

    def authenticate(self) -> None:
        """Authenticate and store the access token."""
        token_url = "/auth/oauth2/token"
        data = {
            "grant_type": "password",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "username": self.username,
            "password": self.password,
        }
        response = self._client.post(token_url, data=data)
        response.raise_for_status()
        self._access_token = response.json().get("access_token")

    def _headers(self) -> Dict[str, str]:
        if not self._access_token:
            raise RuntimeError("Client is not authenticated")
        return {"Authorization": f"Bearer {self._access_token}"}

    def get_picklists(self) -> List[Dict[str, Any]]:
        """Return available picklists."""
        url = f"/api/{self.api_version}/metadata/picklists"
        resp = self._client.get(url, headers=self._headers())
        resp.raise_for_status()
        return resp.json().get("data", [])

    def get_object_metadata(self, object_name: str) -> Dict[str, Any]:
        """Return metadata for a specific object."""
        url = f"/api/{self.api_version}/metadata/objects/{object_name}"
        resp = self._client.get(url, headers=self._headers())
        resp.raise_for_status()
        return resp.json().get("data", {})

    def upsert_object(self, object_name: str, record: Mapping[str, Any]) -> Dict[str, Any]:
        """Create or update a record for the given object."""
        url = f"/api/{self.api_version}/objects/{object_name}"
        resp = self._client.post(url, headers=self._headers(), json=record)
        resp.raise_for_status()
        return resp.json().get("data", {})


class MappingInterface:
    """Utility helpers for mapping iMednet data to Vault objects."""

    def __init__(self, veeva_fields: Iterable[str]) -> None:
        self.veeva_fields = list(veeva_fields)

    def dropdown_options(self, imednet_fields: Iterable[str]) -> Dict[str, List[str]]:
        """Return dropdown options for UI selection."""
        return {field: self.veeva_fields for field in imednet_fields}

    @staticmethod
    def apply_mapping(record: Mapping[str, Any], mapping: Mapping[str, str]) -> Dict[str, Any]:
        """Return a new dict with fields renamed using the provided mapping."""
        return {mapping.get(k, k): v for k, v in record.items()}


def get_required_fields_and_picklists(
    client: VeevaVaultClient, object_name: str, object_type: str | None = None
) -> Tuple[set[str], Dict[str, List[str]], Dict[str, str | None]]:
    """Return required field names, picklist options and defaults for an object."""

    metadata = client.get_object_metadata(object_name)
    fields: List[Dict[str, Any]] = list(metadata.get("fields", []))

    if object_type:
        for ot in metadata.get("objectTypes", []):
            if ot.get("name") == object_type:
                fields.extend(ot.get("fields", []))

    required: set[str] = set()
    picklists: Dict[str, List[str]] = {}
    defaults: Dict[str, str | None] = {}

    for field in fields:
        name = field.get("name")
        if not name:
            continue
        if field.get("required"):
            required.add(name)

        picklist = field.get("picklist") or {}
        values = picklist.get("values")
        if values:
            picklists[name] = [v.get("name") for v in values if "name" in v]
            defaults[name] = picklist.get("defaultValue")

    return required, picklists, defaults


def validate_record_for_upsert(
    client: VeevaVaultClient,
    object_name: str,
    record: MutableMapping[str, Any],
    object_type: str | None = None,
) -> MutableMapping[str, Any]:
    """Validate record fields against object metadata."""

    required, picklists, defaults = get_required_fields_and_picklists(
        client, object_name, object_type
    )

    for field, options in picklists.items():
        if field in record:
            if record[field] not in options:
                raise ValueError(f"Invalid value '{record[field]}' for field '{field}'")
        elif defaults.get(field) is not None:
            record[field] = defaults[field]

    missing = [f for f in required if f not in record]
    if missing:
        raise ValueError(f"Missing required fields: {', '.join(missing)}")

    return record
