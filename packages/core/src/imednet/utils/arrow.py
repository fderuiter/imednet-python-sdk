"""PyArrow serialization helpers."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Protocol

try:
    import pyarrow as pa
except ImportError:  # pragma: no cover - exercised when optional dependency is absent
    pa = None  # type: ignore


class _ModelDumpable(Protocol):
    """Protocol for objects that can be dumped to a dictionary (e.g., Pydantic models)."""

    def model_dump(self) -> Dict[str, Any]: ...


_TRUE_STRINGS = {"true", "1", "yes", "y", "t"}
_FALSE_STRINGS = {"false", "0", "no", "n", "f"}


def _normalize_datetime(value: datetime) -> datetime:
    """Ensure a datetime object is timezone-aware and set to UTC."""
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def _normalize_record(record: Any) -> Dict[str, Any]:
    """Convert an input record (dict or model) into a standard dictionary."""
    if isinstance(record, dict):
        return record

    model_dump = getattr(record, "model_dump", None)
    if callable(model_dump):
        dumped = model_dump()
        if isinstance(dumped, dict):
            return dumped

    raise TypeError("Each record must be a dictionary or expose model_dump().")


def _normalize_value(value: Any) -> Any:
    """Normalize individual values for Arrow serialization (empty strings to None, etc.)."""
    if value is None:
        return None
    if isinstance(value, str) and value == "":
        return None
    if isinstance(value, datetime):
        return _normalize_datetime(value)
    if isinstance(value, bool):
        return bool(value)
    if isinstance(value, float):
        return float(value)
    return value


def _infer_type(values: List[Any]) -> pa.DataType:
    """Infer the Arrow data type from a list of normalized values."""
    non_null_values = [v for v in values if v is not None]
    if not non_null_values:
        return pa.null()
    if all(isinstance(v, bool) for v in non_null_values):
        return pa.bool_()
    if all(isinstance(v, datetime) for v in non_null_values):
        return pa.timestamp("us")
    if all(isinstance(v, float) for v in non_null_values):
        return pa.float64()
    return pa.infer_type(non_null_values)


def _coerce_value(value: Any, target_type: pa.DataType) -> Any:
    """Coerce a value to the target Arrow data type."""
    if value is None:
        return None
    if pa.types.is_null(target_type):
        return None
    if pa.types.is_timestamp(target_type):
        return value if isinstance(value, datetime) else None
    if pa.types.is_boolean(target_type):
        if isinstance(value, str):
            lowered = value.strip().lower()
            if lowered in _TRUE_STRINGS:
                return True
            if lowered in _FALSE_STRINGS:
                return False
            return None
        return bool(value)
    if pa.types.is_floating(target_type):
        try:
            return float(value)
        except (TypeError, ValueError):
            return None
    return value


def to_arrow_table(
    data_records: List[Dict[str, Any] | _ModelDumpable],
    schema: Optional[pa.Schema] = None,
) -> pa.Table:
    """Serialize record dictionaries (or Pydantic-like objects) into a ``pyarrow.Table``.

    Args:
        data_records: Record payloads to serialize. Each item must be a dictionary
            or expose a ``model_dump()`` method that returns a dictionary.
        schema: Optional explicit Arrow schema. When provided, output columns follow
            schema order and types; when omitted, columns and types are inferred.
            Naive ``datetime`` values are interpreted as UTC.
            When schema inference is used, datetime columns use microsecond precision.
            Boolean strings accept ``true/false``, ``1/0``, ``yes/no``, ``y/n``,
            and ``t/f``.

    Returns:
        A fully initialized ``pyarrow.Table`` with deterministic columns and null
        values for missing or empty-string inputs.

    Raises:
        ImportError: If ``pyarrow`` is not installed.
        TypeError: If a record is not dict-like and does not expose ``model_dump``.
    """
    if pa is None:
        raise ImportError(
            "pyarrow is required for to_arrow_table. Install with \"pip install 'imednet[export]'\"."
        )

    records = [_normalize_record(record) for record in data_records]

    if schema is None:
        if not records:
            return pa.table({})
        column_names = sorted({key for record in records for key in record})
    else:
        column_names = list(schema.names)

    arrays: List[pa.Array] = []
    for name in column_names:
        values = [_normalize_value(record.get(name)) for record in records]
        target_type = (
            schema.field(name).type if schema is not None else _infer_type(values)
        )
        arrays.append(
            pa.array(
                [_coerce_value(value, target_type) for value in values],
                type=target_type,
            )
        )

    if schema is not None:
        return pa.Table.from_arrays(arrays, schema=schema)
    return pa.Table.from_arrays(arrays, names=column_names)
