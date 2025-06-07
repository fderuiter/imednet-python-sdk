"""Simple client and mapping helpers for Veeva Vault API."""

from __future__ import annotations

from typing import Any, Callable, Dict, Iterable, List, Mapping, MutableMapping, Tuple, cast

import httpx
from tenacity import (
    AsyncRetrying,
    RetryCallState,
    RetryError,
    Retrying,
    stop_after_attempt,
    wait_exponential,
)

from .mapping import MappingConfig

_METADATA_CACHE: dict[
    tuple[str, str | None], tuple[set[str], dict[str, list[str]], dict[str, str | None]]
] = {}


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
        *,
        timeout: float | httpx.Timeout = 30.0,
        retries: int = 3,
        backoff_factor: float = 1.0,
    ) -> None:
        self.vault = vault
        self.client_id = client_id
        self.client_secret = client_secret
        self.username = username
        self.password = password
        self.base_url = base_url or self.DEFAULT_BASE_URL.format(vault=vault)
        self.api_version = api_version
        self.timeout = timeout if isinstance(timeout, httpx.Timeout) else httpx.Timeout(timeout)
        self.retries = retries
        self.backoff_factor = backoff_factor
        self._access_token: str | None = None
        self._client = httpx.Client(base_url=self.base_url, timeout=self.timeout)

    def _should_retry(self, retry_state: RetryCallState) -> bool:
        if retry_state.outcome is None:
            return False
        exc = retry_state.outcome.exception()
        return isinstance(exc, httpx.RequestError)

    def _request(self, method: str, url: str, **kwargs: Any) -> httpx.Response:
        retryer = Retrying(
            stop=stop_after_attempt(self.retries),
            wait=wait_exponential(multiplier=self.backoff_factor),
            retry=self._should_retry,
            reraise=True,
        )
        try:
            response: httpx.Response = retryer(lambda: self._client.request(method, url, **kwargs))
        except RetryError as exc:
            raise httpx.RequestError("Network request failed after retries") from exc
        response.raise_for_status()
        return response

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
        resp = self._request("GET", url, headers=self._headers())
        return resp.json().get("data", [])

    def get_object_metadata(self, object_name: str) -> Dict[str, Any]:
        """Return metadata for a specific object."""
        url = f"/api/{self.api_version}/metadata/objects/{object_name}"
        resp = self._request("GET", url, headers=self._headers())
        return resp.json().get("data", {})

    def get_object_type_details(self, object_name: str, object_type: str) -> Dict[str, Any]:
        """Return metadata for a specific object type."""
        url = f"/api/{self.api_version}/configuration/Objecttype.{object_name}.{object_type}"
        resp = self._request("GET", url, headers=self._headers())
        return resp.json().get("data", {})

    def get_object_type_configuration(self, object_name: str, object_type: str) -> Dict[str, Any]:
        """Return configuration for an object type."""
        url = f"/api/{self.api_version}/configuration/{object_name}.{object_type}"
        resp = self._request("GET", url, headers=self._headers())
        return resp.json().get("data", {})

    def get_picklist_values(self, picklist_name: str) -> List[Dict[str, Any]]:
        """Return picklist values for the given picklist."""
        url = f"/api/{self.api_version}/objects/picklists/{picklist_name}"
        resp = self._request("GET", url, headers=self._headers())
        return resp.json().get("picklistValues", [])

    def get_object_field_metadata(self, object_name: str, field_name: str) -> Dict[str, Any]:
        """Return metadata for a specific field of an object."""
        url = f"/api/{self.api_version}/metadata/vobjects/{object_name}/fields/{field_name}"
        resp = self._request("GET", url, headers=self._headers())
        return resp.json().get("field", {})

    def collect_required_fields_and_picklists(
        self, object_name: str, object_type: str | None = None
    ) -> Dict[str, Any]:
        """Return required fields and picklist values for an object."""

        metadata = self.get_object_metadata(object_name)
        fields: List[Dict[str, Any]] = list(metadata.get("fields", []))

        if object_type:
            type_details = self.get_object_type_configuration(object_name, object_type)
            type_fields = type_details.get("fields") or type_details.get("type_fields", [])
            fields.extend(type_fields)

        required_fields: List[str] = []
        picklists: Dict[str, List[str]] = {}

        for field in fields:
            name = field.get("name")
            if not name:
                continue

            if field.get("required"):
                required_fields.append(name)

            field_type = str(field.get("type", "")).lower()
            if "picklist" in field_type:
                picklist_name = field.get("picklist")
                if isinstance(picklist_name, dict):
                    picklist_name = picklist_name.get("name")
                if isinstance(picklist_name, str):
                    raw_values = self.get_picklist_values(picklist_name)
                    picklists[name] = [str(v["name"]) for v in raw_values if "name" in v]

        return {"required_fields": required_fields, "picklists": picklists}

    def upsert_object(self, object_name: str, record: Mapping[str, Any]) -> Dict[str, Any]:
        """Create or update a record for the given object."""
        url = f"/api/{self.api_version}/objects/{object_name}"
        resp = self._request("POST", url, headers=self._headers(), json=record)
        return resp.json().get("data", {})

    def bulk_upsert_objects(
        self,
        object_name: str,
        records: Iterable[Mapping[str, Any]],
        *,
        id_param: str | None = None,
        migration_mode: bool = False,
        no_triggers: bool = False,
    ) -> List[Mapping[str, Any]]:
        """Create or update multiple records in bulk."""
        url = f"/api/{self.api_version}/vobjects/{object_name}"
        params = {"idParam": id_param} if id_param else None
        headers = self._headers()
        if migration_mode:
            headers["X-VaultAPI-MigrationMode"] = "true"
            if no_triggers:
                headers["X-VaultAPI-NoTriggers"] = "true"
        resp = self._request("POST", url, headers=headers, params=params, json=list(records))
        return resp.json().get("data", [])

    def bulk_update_objects(
        self,
        object_name: str,
        records: Iterable[Mapping[str, Any]],
        *,
        id_param: str | None = None,
        migration_mode: bool = False,
        no_triggers: bool = False,
    ) -> List[Mapping[str, Any]]:
        """Update multiple records in bulk."""
        url = f"/api/{self.api_version}/vobjects/{object_name}"
        params = {"idParam": id_param} if id_param else None
        headers = self._headers()
        if migration_mode:
            headers["X-VaultAPI-MigrationMode"] = "true"
            if no_triggers:
                headers["X-VaultAPI-NoTriggers"] = "true"
        resp = self._request("PUT", url, headers=headers, params=params, json=list(records))
        return resp.json().get("data", [])

    def upload_attachment(self, file_path: str) -> str:
        """Upload a file to the staging server and return its path."""
        url = f"/api/{self.api_version}/objects/file_staging"
        with open(file_path, "rb") as f:
            resp = self._request("POST", url, headers=self._headers(), files={"file": f})
        return resp.json().get("data", {}).get("file")


class MappingInterface:
    """Utility helpers for mapping iMednet data to Vault objects."""

    def __init__(self, veeva_fields: Iterable[str]) -> None:
        self.veeva_fields = list(veeva_fields)

    def dropdown_options(self, imednet_fields: Iterable[str]) -> Dict[str, List[str]]:
        """Return dropdown options for UI selection."""
        return {field: self.veeva_fields for field in imednet_fields}

    @staticmethod
    def apply_mapping(
        record: Mapping[str, Any],
        mapping: Mapping[str, str] | MappingConfig,
        *,
        transforms: Mapping[str, Callable[[Any], Any]] | None = None,
        defaults: Mapping[str, Any] | None = None,
    ) -> Dict[str, Any]:
        """Return a new dict with fields renamed using the provided mapping."""

        if isinstance(mapping, MappingConfig):
            transforms = mapping.transforms
            defaults = mapping.defaults
            mapping = mapping.mapping

        result: Dict[str, Any] = {}
        for key, value in record.items():
            target = mapping.get(key, key)
            if transforms and key in transforms:
                value = transforms[key](value)
            result[target] = value
        if defaults:
            for key, val in defaults.items():
                result.setdefault(key, val)
        return result


def get_required_fields_and_picklists(
    client: VeevaVaultClient, object_name: str, object_type: str | None = None
) -> Tuple[set[str], Dict[str, List[str]], Dict[str, str | None]]:
    """Return required field names, picklist options and defaults for an object."""
    cache_key = (object_name, object_type)
    if cache_key in _METADATA_CACHE:
        return _METADATA_CACHE[cache_key]

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

    result = (required, picklists, defaults)
    _METADATA_CACHE[cache_key] = result
    return result


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


def collect_required_fields_and_picklists(
    client: VeevaVaultClient, object_name: str, object_type: str | None = None
) -> Dict[str, Any]:
    """Return required fields and picklist values for an object."""

    return client.collect_required_fields_and_picklists(object_name, object_type)


class AsyncVeevaVaultClient(VeevaVaultClient):
    """Asynchronous variant of :class:`VeevaVaultClient`."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # type: ignore[override]
        super().__init__(*args, **kwargs)
        self._client = httpx.AsyncClient(base_url=self.base_url, timeout=self.timeout)  # type: ignore[assignment]

    async def aclose(self) -> None:
        await cast(httpx.AsyncClient, self._client).aclose()

    async def authenticate(self) -> None:  # type: ignore[override]
        token_url = "/auth/oauth2/token"
        data = {
            "grant_type": "password",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "username": self.username,
            "password": self.password,
        }
        resp = await self._request("POST", token_url, data=data)
        self._access_token = resp.json().get("access_token")

    async def _request(self, method: str, url: str, **kwargs: Any) -> httpx.Response:  # type: ignore[override]
        retryer = AsyncRetrying(
            stop=stop_after_attempt(self.retries),
            wait=wait_exponential(multiplier=self.backoff_factor),
            retry=self._should_retry,
            reraise=True,
        )

        async def do_request() -> httpx.Response:
            return await cast(httpx.AsyncClient, self._client).request(method, url, **kwargs)

        try:
            response: httpx.Response = await retryer(do_request)  # type: ignore[misc]
        except RetryError as exc:
            raise httpx.RequestError("Network request failed after retries") from exc
        response.raise_for_status()
        return response

    async def bulk_upsert_objects(  # type: ignore[override]
        self,
        object_name: str,
        records: Iterable[Mapping[str, Any]],
        *,
        id_param: str | None = None,
        migration_mode: bool = False,
        no_triggers: bool = False,
    ) -> List[Mapping[str, Any]]:
        url = f"/api/{self.api_version}/vobjects/{object_name}"
        params = {"idParam": id_param} if id_param else None
        headers = self._headers()
        if migration_mode:
            headers["X-VaultAPI-MigrationMode"] = "true"
            if no_triggers:
                headers["X-VaultAPI-NoTriggers"] = "true"
        resp = await self._request("POST", url, headers=headers, params=params, json=list(records))
        return resp.json().get("data", [])

    async def bulk_update_objects(  # type: ignore[override]
        self,
        object_name: str,
        records: Iterable[Mapping[str, Any]],
        *,
        id_param: str | None = None,
        migration_mode: bool = False,
        no_triggers: bool = False,
    ) -> List[Mapping[str, Any]]:
        url = f"/api/{self.api_version}/vobjects/{object_name}"
        params = {"idParam": id_param} if id_param else None
        headers = self._headers()
        if migration_mode:
            headers["X-VaultAPI-MigrationMode"] = "true"
            if no_triggers:
                headers["X-VaultAPI-NoTriggers"] = "true"
        resp = await self._request("PUT", url, headers=headers, params=params, json=list(records))
        return resp.json().get("data", [])

    async def upload_attachment(self, file_path: str) -> str:  # type: ignore[override]
        url = f"/api/{self.api_version}/objects/file_staging"
        with open(file_path, "rb") as f:
            resp = await self._request("POST", url, headers=self._headers(), files={"file": f})
        return resp.json().get("data", {}).get("file")
