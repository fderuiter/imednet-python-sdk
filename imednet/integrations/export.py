"""Export helpers built on top of :class:`RecordMapper`."""

from __future__ import annotations

from typing import Any, Literal

import pandas as pd

from ..sdk import ImednetSDK
from ..workflows.record_mapper import RecordMapper


def export_to_parquet(sdk: ImednetSDK, study_key: str, path: str, **kwargs: Any) -> None:
    """Export study records to a Parquet file."""
    df: pd.DataFrame = RecordMapper(sdk).dataframe(study_key)
    df.to_parquet(path, index=False, **kwargs)


def export_to_csv(sdk: ImednetSDK, study_key: str, path: str, **kwargs: Any) -> None:
    """Export study records to a CSV file."""
    df: pd.DataFrame = RecordMapper(sdk).dataframe(study_key)
    df.to_csv(path, index=False, **kwargs)


def export_to_excel(sdk: ImednetSDK, study_key: str, path: str, **kwargs: Any) -> None:
    """Export study records to an Excel workbook."""
    df: pd.DataFrame = RecordMapper(sdk).dataframe(study_key)
    df.to_excel(path, index=False, **kwargs)


def export_to_json(sdk: ImednetSDK, study_key: str, path: str, **kwargs: Any) -> None:
    """Export study records to a JSON file."""
    df: pd.DataFrame = RecordMapper(sdk).dataframe(study_key)
    df.to_json(path, index=False, **kwargs)


def export_to_sql(
    sdk: ImednetSDK,
    study_key: str,
    table: str,
    conn_str: str,
    if_exists: Literal["fail", "replace", "append"] = "replace",
    **kwargs: Any,
) -> None:
    """Export study records to a SQL table."""
    from sqlalchemy import create_engine

    df: pd.DataFrame = RecordMapper(sdk).dataframe(study_key)
    engine = create_engine(conn_str)
    df.to_sql(table, engine, if_exists=if_exists, index=False, **kwargs)
