"""Export helpers built on top of :class:`RecordMapper`."""

from __future__ import annotations

from typing import Any, List, Optional

import pandas as pd

from .. import ImednetClient
from ..sdk import ImednetSDK
from ..workflows.record_mapper import RecordMapper

MAX_SQLITE_COLUMNS = 2000


def _to_sql_with_chunking(
    df: pd.DataFrame,
    table: str,
    engine: Any,
    *,
    if_exists: str,
    **kwargs: Any,
) -> None:
    """Write a DataFrame to a SQL table, handling SQLite's column limit by chunking.

    Args:
        df: The DataFrame to write.
        table: The name of the SQL table.
        engine: The SQLAlchemy engine to use.
        if_exists: How to behave if the table already exists.
        **kwargs: Additional keyword arguments to pass to `to_sql`.
    """
    if engine.dialect.name == "sqlite" and len(df.columns) > MAX_SQLITE_COLUMNS:
        for i, start in enumerate(range(0, len(df.columns), MAX_SQLITE_COLUMNS), start=1):
            chunk = df.iloc[:, start : start + MAX_SQLITE_COLUMNS]
            chunk.to_sql(
                f"{table}_part{i}",
                engine,
                if_exists=if_exists,  # type: ignore[arg-type]
                index=False,
                **kwargs,
            )
    else:
        df.to_sql(table, engine, if_exists=if_exists, index=False, **kwargs)  # type: ignore[arg-type]


def _records_df(
    sdk: ImednetSDK,
    study_key: str,
    *,
    use_labels_as_columns: bool = False,
    variable_whitelist: Optional[List[str]] = None,
    form_whitelist: Optional[List[int]] = None,
) -> pd.DataFrame:
    """Fetch records and return them as a DataFrame, handling duplicate columns.

    Args:
        sdk: An initialized ImednetSDK instance.
        study_key: The key of the study.
        use_labels_as_columns: If `True`, use variable labels as column
            headers; otherwise, use variable names.
        variable_whitelist: An optional list of variable names to include.
        form_whitelist: An optional list of form IDs to include.

    Returns:
        A pandas DataFrame of the records.
    """
    df: pd.DataFrame = RecordMapper(sdk).dataframe(
        study_key,
        use_labels_as_columns=use_labels_as_columns,
        variable_whitelist=variable_whitelist,
        form_whitelist=form_whitelist,
    )
    if isinstance(df, pd.DataFrame):
        df.columns = df.columns.astype(str)
        df = df.loc[:, ~df.columns.str.lower().duplicated()]
    return df


def export_to_parquet(
    sdk: ImednetSDK,
    study_key: str,
    path: str,
    *,
    use_labels_as_columns: bool = False,
    **kwargs: Any,
) -> None:
    """Export study records to a Parquet file.

    Args:
        sdk: An initialized ImednetSDK instance.
        study_key: The key of the study.
        path: The path to the output Parquet file.
        use_labels_as_columns: If `True`, use variable labels as column
            headers; otherwise, use variable names.
        **kwargs: Additional keyword arguments to pass to `to_parquet`.
    """
    df = _records_df(
        sdk,
        study_key,
        use_labels_as_columns=use_labels_as_columns,
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

    Args:
        sdk: An initialized ImednetSDK instance.
        study_key: The key of the study.
        path: The path to the output CSV file.
        use_labels_as_columns: If `True`, use variable labels as column
            headers; otherwise, use variable names.
        **kwargs: Additional keyword arguments to pass to `to_csv`.
    """
    df = _records_df(
        sdk,
        study_key,
        use_labels_as_columns=use_labels_as_columns,
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

    Args:
        sdk: An initialized ImednetSDK instance.
        study_key: The key of the study.
        path: The path to the output Excel file.
        use_labels_as_columns: If `True`, use variable labels as column
            headers; otherwise, use variable names.
        **kwargs: Additional keyword arguments to pass to `to_excel`.
    """
    df = _records_df(
        sdk,
        study_key,
        use_labels_as_columns=use_labels_as_columns,
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

    Args:
        sdk: An initialized ImednetSDK instance.
        study_key: The key of the study.
        path: The path to the output JSON file.
        use_labels_as_columns: If `True`, use variable labels as column
            headers; otherwise, use variable names.
        **kwargs: Additional keyword arguments to pass to `to_json`.
    """
    df = _records_df(
        sdk,
        study_key,
        use_labels_as_columns=use_labels_as_columns,
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
    variable_whitelist: Optional[List[str]] = None,
    form_whitelist: Optional[List[int]] = None,
    **kwargs: Any,
) -> None:
    """Export study records to a SQL table.

    Args:
        sdk: An initialized ImednetSDK instance.
        study_key: The key of the study.
        table: The name of the SQL table.
        conn_str: The SQLAlchemy connection string.
        if_exists: How to behave if the table already exists.
        use_labels_as_columns: If `True`, use variable labels as column
            headers; otherwise, use variable names.
        variable_whitelist: An optional list of variable names to include.
        form_whitelist: An optional list of form IDs to include.
        **kwargs: Additional keyword arguments to pass to `to_sql`.
    """
    from sqlalchemy import create_engine

    df = _records_df(
        sdk,
        study_key,
        use_labels_as_columns=use_labels_as_columns,
        variable_whitelist=variable_whitelist,
        form_whitelist=form_whitelist,
    )
    engine = create_engine(conn_str)
    _to_sql_with_chunking(
        df,
        table,
        engine,
        if_exists=if_exists,
        **kwargs,
    )  # type: ignore[arg-type]


def export_to_sql_by_form(
    sdk: ImednetSDK,
    study_key: str,
    conn_str: str,
    if_exists: str = "replace",
    *,
    use_labels_as_columns: bool = False,
    variable_whitelist: Optional[List[str]] = None,
    form_whitelist: Optional[List[int]] = None,
    **kwargs: Any,
) -> None:
    """Export records to separate SQL tables for each form.

    Args:
        sdk: An initialized ImednetSDK instance.
        study_key: The key of the study.
        conn_str: The SQLAlchemy connection string.
        if_exists: How to behave if the table already exists.
        use_labels_as_columns: If `True`, use variable labels as column
            headers; otherwise, use variable names.
        variable_whitelist: An optional list of variable names to include.
        form_whitelist: An optional list of form IDs to include.
        **kwargs: Additional keyword arguments to pass to `to_sql`.
    """
    from sqlalchemy import create_engine

    mapper = RecordMapper(sdk)
    engine = create_engine(conn_str)
    forms = sdk.forms.list(study_key=study_key)
    for form in forms:
        if form_whitelist is not None and form.form_id not in form_whitelist:
            continue
        variables = sdk.variables.list(study_key=study_key, formId=form.form_id)
        variable_keys = [
            v.variable_name
            for v in variables
            if variable_whitelist is None or v.variable_name in variable_whitelist
        ]
        label_map = {
            v.variable_name: v.label for v in variables if v.variable_name in variable_keys
        }
        record_model = mapper._build_record_model(variable_keys, label_map)
        records = mapper._fetch_records(
            study_key,
            extra_filters={
                "formId": form.form_id,
                **({"variableNames": variable_keys} if variable_whitelist else {}),
            },
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
        _to_sql_with_chunking(
            df,
            form.form_key,
            engine,
            if_exists=if_exists,
            **kwargs,
        )  # type: ignore[arg-type]


def export_to_long_sql(
    sdk: ImednetClient,
    study_key: str,
    table_name: str,
    conn_str: str,
    *,
    chunk_size: int = 1000,
) -> None:
    """Export records to a normalized long-format SQL table.

    This format is useful for data analysis and is more normalized than the
    wide format.

    Args:
        sdk: An initialized ImednetClient instance.
        study_key: The key of the study.
        table_name: The name of the SQL table.
        conn_str: The SQLAlchemy connection string.
        chunk_size: The number of rows to write to the database at a time.
    """
    from sqlalchemy import create_engine

    engine = create_engine(conn_str)
    mapper = RecordMapper(sdk)
    records = mapper._fetch_records(study_key)

    rows: List[dict[str, Any]] = []
    first = True
    for rec in records:
        timestamp = rec.date_modified
        for name, value in (rec.record_data or {}).items():
            rows.append(
                {
                    "record_id": rec.record_id,
                    "form_id": rec.form_id,
                    "variable_name": name,
                    "value": value,
                    "timestamp": timestamp,
                }
            )
            if len(rows) >= chunk_size:
                df = pd.DataFrame(rows)
                df.to_sql(
                    table_name,
                    engine,
                    if_exists="replace" if first else "append",
                    index=False,
                )
                rows = []
                first = False
    if rows:
        df = pd.DataFrame(rows)
        df.to_sql(
            table_name,
            engine,
            if_exists="replace" if first else "append",
            index=False,
        )
