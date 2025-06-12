"""Helpers for exporting study data to various formats."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..utils import records_to_dataframe

if TYPE_CHECKING:  # pragma: no cover - used for type hints only
    from ..sdk import ImednetSDK


def export_csv(sdk: "ImednetSDK", study_key: str, path: str, *, flatten: bool = True) -> None:
    """Export study records to a CSV file."""
    records = sdk.records.list(study_key=study_key)
    df = records_to_dataframe(records, flatten=flatten)
    df.to_csv(path, index=False)


def export_excel(sdk: "ImednetSDK", study_key: str, path: str, *, flatten: bool = True) -> None:
    """Export study records to an Excel file."""
    records = sdk.records.list(study_key=study_key)
    df = records_to_dataframe(records, flatten=flatten)
    df.to_excel(path, index=False)


def export_json(sdk: "ImednetSDK", study_key: str, path: str, *, flatten: bool = True) -> None:
    """Export study records to a JSON file."""
    records = sdk.records.list(study_key=study_key)
    df = records_to_dataframe(records, flatten=flatten)
    df.to_json(path, orient="records", indent=2)


def export_parquet(sdk: "ImednetSDK", study_key: str, path: str, *, flatten: bool = True) -> None:
    """Export study records to a Parquet file."""
    records = sdk.records.list(study_key=study_key)
    df = records_to_dataframe(records, flatten=flatten)
    df.to_parquet(path, index=False)


def export_sql(
    sdk: "ImednetSDK",
    study_key: str,
    table: str,
    connection_string: str,
    *,
    flatten: bool = True,
    if_exists: str = "replace",
) -> None:
    """Export study records to a SQL table using ``pandas.to_sql``."""
    records = sdk.records.list(study_key=study_key)
    df = records_to_dataframe(records, flatten=flatten)
    from sqlalchemy import create_engine

    engine = create_engine(connection_string)
    with engine.begin() as conn:
        df.to_sql(table, conn, if_exists=if_exists, index=False)
