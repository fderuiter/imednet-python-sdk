"""Airflow hook for retrieving an :class:`ImednetSDK` instance."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from pathlib import PurePosixPath
from typing import Any

from .._airflow_compat import AirflowBaseHook

from imednet.config import load_config
from imednet.sdk import ImednetSDK

# JSON/XCom-safe scalar types.
Primitive = str | int | float | bool | None
# JSON/XCom-safe nested payload types.
PrimitiveValue = Primitive | list["PrimitiveValue"] | dict[str, "PrimitiveValue"]


class ImednetHook(AirflowBaseHook):
    """Retrieve an :class:`ImednetSDK` instance from an Airflow connection."""

    def __init__(self, imednet_conn_id: str = "imednet_default") -> None:
        super().__init__()
        self.imednet_conn_id = imednet_conn_id

    def get_conn(self) -> ImednetSDK:  # type: ignore[override]
        conn = AirflowBaseHook.get_connection(self.imednet_conn_id)
        extras = self._connection_extras(conn)
        login = self._string_or_none(getattr(conn, "login", None))
        password = self._string_or_none(getattr(conn, "password", None))
        api_key = self._first_non_empty_string(extras.get("api_key"), login)
        security_key = self._first_non_empty_string(extras.get("security_key"), password)
        base_url = self._string_or_none(extras.get("base_url"))
        config = load_config(
            api_key=api_key,
            security_key=security_key,
            base_url=base_url,
        )
        return ImednetSDK(
            api_key=config.api_key,
            security_key=config.security_key,
            base_url=config.base_url,
        )

    def get_sdk_client(self) -> ImednetSDK:
        """Return an SDK client for use inside task execution context."""
        return self.get_conn()

    def resolved_connection_config(self, *, redact_credentials: bool = True) -> dict[str, str]:
        """Return resolved connection settings as serialization-safe primitives."""
        sdk = self.get_sdk_client()
        config = sdk.config
        api_key = config.api_key
        security_key = config.security_key
        settings = {
            "api_key": self._redact_secret(api_key) if redact_credentials else api_key,
            "security_key": (
                self._redact_secret(security_key) if redact_credentials else security_key
            ),
            "base_url": config.base_url,
        }
        return {k: str(v) for k, v in settings.items() if v is not None}

    def discover_studies(self, *, active_only: bool = True) -> list[dict[str, PrimitiveValue]]:
        """Return primitive study metadata for dynamic task mapping."""
        sdk = self.get_sdk_client()
        studies = sdk.studies.list()
        payload: list[dict[str, PrimitiveValue]] = []
        for study in studies:
            item = self._to_mapping(study)
            study_key = self._string_or_none(item.get("study_key"))
            if not study_key:
                continue
            is_active = self._coerce_bool(item.get("active"))
            if is_active is None:
                is_active = self._coerce_bool(item.get("is_active"))
            if is_active is None:
                status = self._string_or_none(item.get("status"))
                if status:
                    is_active = status.upper() == "ACTIVE"
            if active_only and is_active is False:
                continue
            payload.append(
                {
                    "study_key": study_key,
                    "study_name": self._string_or_none(item.get("study_name")),
                    "is_active": is_active,
                }
            )
        return payload

    def build_export_requests(
        self,
        *,
        output_root: str,
        file_extension: str = "csv",
        active_only: bool = True,
    ) -> list[dict[str, str]]:
        """Return primitive mapped kwargs payloads for export operators."""
        ext = file_extension.lstrip(".") or "csv"
        root = PurePosixPath(output_root)
        studies = self.discover_studies(active_only=active_only)
        return [
            {
                "study_key": str(study["study_key"]),
                "output_path": str(root / f"{study['study_key']}.{ext}"),
            }
            for study in studies
        ]

    @staticmethod
    def _connection_extras(conn: Any) -> Mapping[str, Any]:
        extras = getattr(conn, "extra_dejson", {}) or {}
        if isinstance(extras, Mapping):
            return extras
        return {}

    @staticmethod
    def _string_or_none(value: Any) -> str | None:
        if value is None:
            return None
        if isinstance(value, str):
            return value or None
        return str(value)

    @staticmethod
    def _first_non_empty_string(*values: Any) -> str | None:
        for value in values:
            normalized = ImednetHook._string_or_none(value)
            if normalized:
                return normalized
        return None

    @staticmethod
    def _redact_secret(value: str | None) -> str | None:
        if value is None:
            return None
        return "***"

    @staticmethod
    def _to_mapping(value: Any) -> Mapping[str, PrimitiveValue]:
        if isinstance(value, Mapping):
            mapping: dict[str, PrimitiveValue] = {}
            for key, item in value.items():
                if isinstance(key, str):
                    mapping[key] = ImednetHook._to_primitive(item)
            return mapping
        data = getattr(value, "model_dump", None)
        if callable(data):
            try:
                dumped = data()
            except (AttributeError, TypeError, ValueError):  # pragma: no cover
                dumped = None
            if isinstance(dumped, Mapping):
                return ImednetHook._to_mapping(dumped)
        attrs: dict[str, PrimitiveValue] = {}
        for field in ("study_key", "study_name", "active", "is_active", "status"):
            if hasattr(value, field):
                attrs[field] = ImednetHook._to_primitive(getattr(value, field))
        return attrs

    @staticmethod
    def _to_primitive(value: Any) -> PrimitiveValue:
        if value is None or isinstance(value, (str, int, float, bool)):
            return value
        if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
            return [ImednetHook._to_primitive(item) for item in value]
        if isinstance(value, Mapping):
            return {
                str(key): ImednetHook._to_primitive(item)
                for key, item in value.items()
                if isinstance(key, str)
            }
        return str(value)

    @staticmethod
    def _coerce_bool(value: PrimitiveValue | Any) -> bool | None:
        """Parse common string/boolean tokens into bool values."""
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            normalized = value.strip().lower()
            if normalized in {"true", "1", "yes", "y"}:
                return True
            if normalized in {"false", "0", "no", "n"}:
                return False
        return None


__all__ = ["ImednetHook"]
