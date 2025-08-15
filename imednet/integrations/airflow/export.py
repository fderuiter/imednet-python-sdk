"""Airflow-facing export helpers."""

from __future__ import annotations

from typing import Any

from .. import export as _base_export


def export_to_csv(*args: Any, **kwargs: Any) -> None:
    return _base_export.export_to_csv(*args, **kwargs)


def export_to_parquet(*args: Any, **kwargs: Any) -> None:
    return _base_export.export_to_parquet(*args, **kwargs)


def export_to_excel(*args: Any, **kwargs: Any) -> None:
    return _base_export.export_to_excel(*args, **kwargs)


def export_to_json(*args: Any, **kwargs: Any) -> None:
    return _base_export.export_to_json(*args, **kwargs)


def export_to_sql(*args: Any, **kwargs: Any) -> None:
    return _base_export.export_to_sql(*args, **kwargs)


def export_to_sql_by_form(*args: Any, **kwargs: Any) -> None:
    return _base_export.export_to_sql_by_form(*args, **kwargs)


__all__ = [
    "export_to_csv",
    "export_to_parquet",
    "export_to_excel",
    "export_to_json",
    "export_to_sql",
    "export_to_sql_by_form",
]
