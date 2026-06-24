"""Airflow hook for retrieving an :class:`ImednetSDK` instance."""

from __future__ import annotations

import json
from datetime import date, datetime
from typing import (
    TYPE_CHECKING,
    Any,
    Dict,
    List,
    Mapping,
    MutableMapping,
    TypeAlias,
    Union,
    cast,
)

if TYPE_CHECKING:
    from airflow.sdk.bases.hook import BaseHook as AirflowBaseHook
else:
    try:
        from airflow.sdk.bases.hook import BaseHook as AirflowBaseHook
    except (ImportError, ModuleNotFoundError):
        try:
            from airflow.hooks.base import BaseHook as AirflowBaseHook  # type: ignore[attr-defined]
        except (ImportError, ModuleNotFoundError):

            class AirflowBaseHook:
                """Fallback for BaseHook when Airflow is not installed."""

                def __init__(self, *args: Any, **kwargs: Any) -> None:
                    pass

                @classmethod
                def get_connection(cls, conn_id: str) -> Any:
                    raise RuntimeError("Airflow is not installed; cannot get connection.")


from imednet import Config, ImednetSDK, load_config

Primitive = Union[str, int, float, bool, None]
# Primitive-only payload contract for discovery helpers that feed Airflow mapping/XCom.
PrimitiveContainer: TypeAlias = Union[
    Primitive, List["PrimitiveContainer"], Dict[str, "PrimitiveContainer"]
]
_SENSITIVE_KEYS = {
    "api_key",
    "security_key",
    "authorization",
    "token",
    "x-api-key",
    "x-imn-security-key",
}


class ImednetHook(AirflowBaseHook):
    """Retrieve an :class:`ImednetSDK` instance from an Airflow connection."""

    def __init__(self, imednet_conn_id: str = "imednet_default") -> None:
        """Initialize the Imednet hook."""
        super().__init__()
        self.imednet_conn_id = imednet_conn_id

    @staticmethod
    def _string_or_none(value: object) -> str | None:
        """Return a stripped string or ``None`` for non-string/blank values."""
        if not isinstance(value, str):
            return None
        cleaned = value.strip()
        return cleaned or None

    @staticmethod
    def _parsed_extras(value: object) -> MutableMapping[str, object] | None:
        """Return parsed connection extras when value is a dict-like payload."""
        if isinstance(value, Mapping):
            return cast(MutableMapping[str, object], dict(value))
        if isinstance(value, str):
            try:
                parsed = json.loads(value)
            except json.JSONDecodeError:
                return None
            if isinstance(parsed, dict):
                return cast(MutableMapping[str, object], parsed)
        return None

    @classmethod
    def _connection_extras(cls, conn: object) -> MutableMapping[str, object]:
        """Resolve extras from Airflow connection objects across API versions."""
        extras = cls._parsed_extras(getattr(conn, "extra_dejson", None))
        if extras is not None:
            return extras

        get_extra = getattr(conn, "get_extra", None)
        if callable(get_extra):
            try:
                raw_extra = get_extra()
            except (AttributeError, TypeError, ValueError):
                raw_extra = None
            extras = cls._parsed_extras(raw_extra)
            if extras is not None:
                return extras

        extras = cls._parsed_extras(getattr(conn, "extra", None))
        if extras is not None:
            return extras
        return {}

    def _resolved_config(self) -> Config:
        """Resolve hook configuration from Airflow connection fields and env fallback."""
        # Use local import to avoid hard dependency on Airflow at module level
        # if not already resolved via AirflowBaseHook.
        base_hook: Any
        try:
            from airflow.sdk.bases.hook import BaseHook as _LocalSDKBaseHook

            base_hook = _LocalSDKBaseHook
        except (ImportError, ModuleNotFoundError):
            try:
                from airflow.hooks.base import (
                    BaseHook as _LocalLegacyBaseHook,  # type: ignore[attr-defined]
                )

                base_hook = _LocalLegacyBaseHook
            except (ImportError, ModuleNotFoundError):
                base_hook = AirflowBaseHook

        conn = base_hook.get_connection(self.imednet_conn_id)
        extras_dict = self._connection_extras(conn)

        config = load_config(
            api_key=self._string_or_none(extras_dict.get("api_key"))
            or self._string_or_none(getattr(conn, "login", None)),
            security_key=self._string_or_none(extras_dict.get("security_key"))
            or self._string_or_none(getattr(conn, "password", None)),
            base_url=self._string_or_none(extras_dict.get("base_url")),
        )
        return config

    @classmethod
    def _to_primitive(cls, value: Any) -> PrimitiveContainer:
        """Recursively normalize values to primitive containers with credential redaction.

        Pydantic-style objects are first converted via ``model_dump(mode="json", by_alias=True)``.
        Dictionaries are traversed recursively and sensitive keys are masked. Unknown
        object types fall back to ``str(value)`` so discovery outputs remain serializable.
        """
        if value is None or isinstance(value, (str, int, float, bool)):
            return cast(Primitive, value)
        if isinstance(value, (date, datetime)):
            return value.isoformat()
        if hasattr(value, "model_dump"):
            dumped = value.model_dump(mode="json", by_alias=True)
            value = cast(Any, dumped)
        if isinstance(value, Mapping):
            output: Dict[str, PrimitiveContainer] = {}
            for key, item in value.items():
                key_str = str(key)
                if key_str.lower() in _SENSITIVE_KEYS:
                    output[key_str] = "***"
                else:
                    output[key_str] = cls._to_primitive(item)
            return output
        if isinstance(value, (list, tuple, set)):
            return [cls._to_primitive(item) for item in value]
        return str(value)

    def get_sdk_client(self) -> ImednetSDK:
        """Return an SDK client for use within task execution context."""
        config = self._resolved_config()
        return ImednetSDK(
            api_key=config.api_key,
            security_key=config.security_key,
            base_url=config.base_url,
        )

    def get_conn(self) -> ImednetSDK:  # type: ignore[override]
        """Backward compatible alias for :meth:`get_sdk_client`."""
        return self.get_sdk_client()

    def describe_connection(self) -> Dict[str, PrimitiveContainer]:
        """Return redacted primitive metadata about resolved hook configuration."""
        config = self._resolved_config()
        return {
            "imednet_conn_id": self.imednet_conn_id,
            "base_url": self._to_primitive(config.base_url),
            "api_key": "***",
            "security_key": "***",
            "api_key_configured": bool(config.api_key),
            "security_key_configured": bool(config.security_key),
        }

    def list_studies_metadata(self) -> List[Dict[str, PrimitiveContainer]]:
        """Return primitive, serialization-safe study metadata for task mapping."""
        studies = self.get_sdk_client().studies.list()
        metadata: List[Dict[str, PrimitiveContainer]] = []
        for study in studies:
            primitive_study = self._to_primitive(study)
            if isinstance(primitive_study, dict):
                metadata.append(primitive_study)
        return metadata

    def list_study_keys(self) -> List[str]:
        """Return primitive study keys for mapped Airflow task expansion."""
        keys: List[str] = []
        for study in self.list_studies_metadata():
            study_key = study.get("studyKey") or study.get("study_key")
            if isinstance(study_key, str) and study_key:
                keys.append(study_key)
        return keys


__all__ = ["ImednetHook"]
