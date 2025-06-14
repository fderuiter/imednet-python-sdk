"""Export helpers built on top of :class:`RecordMapper`."""

from __future__ import annotations

from typing import Any

import pandas as pd

from ..sdk import ImednetSDK
from ..workflows.record_mapper import RecordMapper


def export_to_parquet(
    sdk: ImednetSDK,
    study_key: str,
    path: str,
    *,
    use_labels_as_columns: bool = False,
    **kwargs: Any,
) -> None:
    """Export study records to a Parquet file.

    Parameters
    ----------
    use_labels_as_columns:
        When ``True``, variable labels are used for column names instead of
        variable names.
    """
    df: pd.DataFrame = RecordMapper(sdk).dataframe(
        study_key, use_labels_as_columns=use_labels_as_columns
    )
    df.to_parquet(path, index=False, **kwargs)


def export_to_csv(
    sdk: ImednetSDK,
    study_key: str,
    path: str,
    *,
    use_labels_as_columns: bool = False,
    **kwargs: Any,
) -> None:
    """Export study records to a CSV file.

    Parameters
    ----------
    use_labels_as_columns:
        When ``True``, variable labels are used for column names instead of
        variable names.
    """
    df: pd.DataFrame = RecordMapper(sdk).dataframe(
        study_key, use_labels_as_columns=use_labels_as_columns
    )
    df.to_csv(path, index=False, **kwargs)


def export_to_excel(
    sdk: ImednetSDK,
    study_key: str,
    path: str,
    *,
    use_labels_as_columns: bool = False,
    **kwargs: Any,
) -> None:
    """Export study records to an Excel workbook.

    Parameters
    ----------
    use_labels_as_columns:
        When ``True``, variable labels are used for column names instead of
        variable names.
    """
    df: pd.DataFrame = RecordMapper(sdk).dataframe(
        study_key, use_labels_as_columns=use_labels_as_columns
    )
    df.to_excel(path, index=False, **kwargs)


def export_to_json(
    sdk: ImednetSDK,
    study_key: str,
    path: str,
    *,
    use_labels_as_columns: bool = False,
    **kwargs: Any,
) -> None:
    """Export study records to a JSON file.

    Parameters
    ----------
    use_labels_as_columns:
        When ``True``, variable labels are used for column names instead of
        variable names.
    """
    df: pd.DataFrame = RecordMapper(sdk).dataframe(
        study_key, use_labels_as_columns=use_labels_as_columns
    )
    df.to_json(path, index=False, **kwargs)


def export_to_sql(
    sdk: ImednetSDK,
    study_key: str,
    table: str,
    conn_str: str,
    if_exists: str = "replace",
    *,
    use_labels_as_columns: bool = False,
    **kwargs: Any,
) -> None:
    """Export study records to a SQL table.

    Parameters
    ----------
    use_labels_as_columns:
        When ``True``, variable labels are used for column names instead of
        variable names.
    """
    from sqlalchemy import create_engine

    df: pd.DataFrame = RecordMapper(sdk).dataframe(
        study_key, use_labels_as_columns=use_labels_as_columns
    )
    engine = create_engine(conn_str)
    df.to_sql(table, engine, if_exists=if_exists, index=False, **kwargs)  # type: ignore[arg-type]
