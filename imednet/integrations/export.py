"""Export helpers built on top of :class:`RecordMapper`."""

from __future__ import annotations

from typing import Any

import pandas as pd

from ..sdk import ImednetSDK
from ..workflows.record_mapper import RecordMapper

MAX_SQLITE_COLUMNS = 2000


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
    if isinstance(df, pd.DataFrame):
        df = df.loc[:, ~df.columns.str.lower().duplicated()]
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
    # Remove duplicate columns which can occur when variable names repeat across
    # forms or revisions. Columns are considered duplicates regardless of case
    # sensitivity. Skip if the object does not expose a pandas-like interface
    # (e.g. unit tests using mocks).
    if isinstance(df, pd.DataFrame):
        dup_mask = df.columns.str.lower().duplicated()
        df = df.loc[:, ~dup_mask]
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
    # Duplicate column names cause ``to_sql`` to raise an error. Trim them here
    # by keeping the first occurrence of each column, ignoring case. Skip when a
    # mock DataFrame is supplied during unit tests.
    if isinstance(df, pd.DataFrame):
        dup_mask = df.columns.str.lower().duplicated()
        df = df.loc[:, ~dup_mask]
    engine = create_engine(conn_str)
    if engine.dialect.name == "sqlite" and len(df.columns) > MAX_SQLITE_COLUMNS:
        raise ValueError(
            "SQLite supports up to "
            f"{MAX_SQLITE_COLUMNS} columns; received {len(df.columns)} columns. "
            "Reduce variables or use another DB."
        )

    df.to_sql(table, engine, if_exists=if_exists, index=False, **kwargs)  # type: ignore[arg-type]


def export_to_sql_by_form(
    sdk: ImednetSDK,
    study_key: str,
    conn_str: str,
    if_exists: str = "replace",
    *,
    use_labels_as_columns: bool = False,
    **kwargs: Any,
) -> None:
    """Export records to separate SQL tables for each form."""
    from sqlalchemy import create_engine

    mapper = RecordMapper(sdk)
    engine = create_engine(conn_str)
    forms = sdk.forms.list(study_key=study_key)
    for form in forms:
        variables = sdk.variables.list(study_key=study_key, formId=form.form_id)
        variable_keys = [v.variable_name for v in variables]
        label_map = {v.variable_name: v.label for v in variables}
        record_model = mapper._build_record_model(variable_keys, label_map)
        records = mapper._fetch_records(
            study_key,
            extra_filters={"formId": form.form_id},
        )
        rows, _ = mapper._parse_records(records, record_model)
        df = mapper._build_dataframe(
            rows,
            variable_keys,
            label_map,
            use_labels_as_columns,
        )
        if isinstance(df, pd.DataFrame):
            dup_mask = df.columns.str.lower().duplicated()
            df = df.loc[:, ~dup_mask]
        if engine.dialect.name == "sqlite" and len(df.columns) > MAX_SQLITE_COLUMNS:
            raise ValueError(
                "SQLite supports up to "
                f"{MAX_SQLITE_COLUMNS} columns; received {len(df.columns)} columns."
                " Reduce variables or use another DB."
            )
        df.to_sql(form.form_key, engine, if_exists=if_exists, index=False, **kwargs)  # type: ignore[arg-type]
