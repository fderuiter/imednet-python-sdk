"""Export helpers built on top of :class:`RecordMapper`."""

from __future__ import annotations

from importlib import import_module
from typing import Any, List, Optional

try:
    import pandas as pd
except ImportError:
    pd = None  # type: ignore
from imednet.constants import MAX_SQLITE_COLUMNS
from imednet.utils import sanitize_csv_formula
from imednet.utils.security import global_sensitivity_registry, mask_clinical_phi

from .. import ImednetClient
from ..sdk import ImednetSDK


def _quote_duckdb_identifier(name: str) -> str:
    escaped_name = name.replace('"', '""')
    return f'"{escaped_name}"'


_DUCKDB_DF_ALIAS = "df"


def _record_mapper() -> Any:
    try:
        return import_module("imednet_workflows.record_mapper").RecordMapper
    except ModuleNotFoundError as error:
        if error.name and error.name.startswith("imednet_workflows"):
            raise ImportError(
                "Record export requires the optional 'imednet-workflows' package. "
                "Install with `pip install imednet-workflows`."
            ) from error
        raise


def _mask_df(df: pd.DataFrame) -> pd.DataFrame:
    """Mask sensitive fields in the DataFrame based on the global registry."""
    sensitive_cols = [
        col for col in df.columns if global_sensitivity_registry.is_sensitive(str(col))
    ]
    for col in sensitive_cols:
        df[col] = "***MASKED***"

    try:
        object_cols = df.drop(columns=sensitive_cols).select_dtypes(include=[object, "str"]).columns
    except TypeError:
        object_cols = df.drop(columns=sensitive_cols).select_dtypes(include=[object]).columns

    for col in object_cols:
        df[col] = df[col].apply(mask_clinical_phi)

    return df


def _to_sql_with_chunking(
    df: pd.DataFrame,
    table: str,
    engine: Any,
    *,
    if_exists: str,
    **kwargs: Any,
) -> None:
    """Write ``df`` to ``table`` splitting columns when using SQLite.

    SQLite limits tables to ``MAX_SQLITE_COLUMNS`` columns. When the DataFrame
    exceeds this, the data is written to multiple tables suffixed with
    ``_part1``, ``_part2`` and so on.
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
    """Return a DataFrame of study records with duplicate columns removed."""
    if pd is None:
        raise ImportError(
            (
                "pandas is required for _records_df. Install with "
                "'pip install pandas imednet-workflows'."
            )
        )
    df: pd.DataFrame = _record_mapper()(sdk).dataframe(
        study_key,
        use_labels_as_columns=use_labels_as_columns,
        variable_whitelist=variable_whitelist,
        form_whitelist=form_whitelist,
    )
    if isinstance(df, pd.DataFrame):
        df.columns = df.columns.astype(str)
        df = df.loc[:, ~df.columns.str.lower().duplicated()]
    return df


def _prepare_export_df(
    sdk: ImednetSDK,
    study_key: str,
    *,
    use_labels_as_columns: bool = False,
    variable_whitelist: Optional[List[str]] = None,
    form_whitelist: Optional[List[int]] = None,
    sanitize: bool = False,
) -> pd.DataFrame:
    """Prepare a DataFrame for export by fetching records and optionally sanitizing."""
    df = _records_df(
        sdk,
        study_key,
        use_labels_as_columns=use_labels_as_columns,
        variable_whitelist=variable_whitelist,
        form_whitelist=form_whitelist,
    )
    df = _mask_df(df)
    if sanitize:
        df = _sanitize_df(df)
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

    All exports now inherit StudyConfiguration rules by default.

    Parameters
    ----------
    use_labels_as_columns:
        When ``True``, variable labels are used for column names instead of
        variable names.
    """
    df = _prepare_export_df(
        sdk,
        study_key,
        use_labels_as_columns=use_labels_as_columns,
    )
    df.to_parquet(path, index=False, **kwargs)


def _sanitize_df(df: pd.DataFrame) -> pd.DataFrame:
    """Sanitize DataFrame string columns to prevent CSV injection."""
    # Explicitly include "str" to avoid Pandas 3.0 warning about object dtype
    # including strings implicitly. Use a try/except block to handle older Pandas versions
    # (e.g. 2.3.3) where "str" raises a TypeError.
    try:
        cols = df.select_dtypes(include=[object, "str"])
    except TypeError:
        cols = df.select_dtypes(include=[object])

    for col in cols:
        df[col] = df[col].apply(sanitize_csv_formula)  # type: ignore[call-overload]
    return df


def export_to_csv(
    sdk: ImednetSDK,
    study_key: str,
    path: str,
    *,
    use_labels_as_columns: bool = False,
    **kwargs: Any,
) -> None:
    """Export study records to a CSV file.

    All exports now inherit StudyConfiguration rules by default.

    Parameters
    ----------
    use_labels_as_columns:
        When ``True``, variable labels are used for column names instead of
        variable names.
    """
    df = _prepare_export_df(
        sdk,
        study_key,
        use_labels_as_columns=use_labels_as_columns,
        sanitize=True,
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

    All exports now inherit StudyConfiguration rules by default.

    Parameters
    ----------
    use_labels_as_columns:
        When ``True``, variable labels are used for column names instead of
        variable names.
    """
    df = _prepare_export_df(
        sdk,
        study_key,
        use_labels_as_columns=use_labels_as_columns,
        sanitize=True,
    )
    df.to_excel(path, index=False, **kwargs)


def export_to_json(
    sdk: ImednetSDK,
    study_key: str,
    path: str,
    *,
    use_labels_as_columns: bool = False,
    hierarchical: bool = False,
    **kwargs: Any,
) -> None:
    """Export study records to a JSON file.

    All exports now inherit StudyConfiguration rules by default.

    Parameters
    ----------
    use_labels_as_columns:
        When ``True``, variable labels are used for column names instead of
        variable names.
    hierarchical:
        When ``True``, generates a nested tree (Subject > Visit > Form) suitable
        for Veeva Vault integrations instead of a flat tabular layout.
    """
    import json
    import logging

    logger = logging.getLogger(__name__)

    if hierarchical:
        mapper = _record_mapper()(sdk)
        data = mapper.build_hierarchy(study_key, use_labels_as_keys=use_labels_as_columns)
    else:
        df = _prepare_export_df(
            sdk,
            study_key,
            use_labels_as_columns=use_labels_as_columns,
        )
        import pandas as pd

        # Explicitly handle missing values when converting to dict
        data = df.where(pd.notnull(df), None).to_dict(orient="records")

    try:
        from importlib import import_module

        config_version_store_cls = import_module(
            "imednet_workflows.config_version_control"
        ).ConfigVersionStore
        enrichment_pipeline_cls = import_module(
            "imednet.integrations.enrichment"
        ).EnrichmentPipeline

        store = config_version_store_cls()
        history = store.get_history(study_key)
        if history:
            latest_commit = history[-1]["commit_id"]
            config = store.rollback_config(study_key, latest_commit)

            logger.info("Enrichment pipeline triggered")
            pipeline = enrichment_pipeline_cls(config)
            data = pipeline.process(data)
            logger.info("Enrichment pipeline completed successfully")
    except Exception as e:
        logger.warning(f"Could not apply EnrichmentPipeline: {e}")

    with open(path, "w") as f:
        json.dump(data, f, **kwargs)


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

    All exports now inherit StudyConfiguration rules by default.

    Parameters
    ----------
    use_labels_as_columns:
        When ``True``, variable labels are used for column names instead of
        variable names.
    """
    from sqlalchemy import create_engine

    df = _prepare_export_df(
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


def export_to_duckdb(
    sdk: ImednetSDK,
    study_key: str,
    db_path: str,
    table_name: str,
    *,
    use_labels_as_columns: bool = False,
    variable_whitelist: Optional[List[str]] = None,
    form_whitelist: Optional[List[int]] = None,
) -> None:
    """Export study records to a DuckDB table using native DataFrame registration.

    All exports now inherit StudyConfiguration rules by default.

    Parameters
    ----------
    sdk:
        Authenticated SDK instance used to fetch study records.
    study_key:
        Study identifier to export.
    db_path:
        Path to the target ``.duckdb`` database file.
    table_name:
        Name of the destination DuckDB table.
    use_labels_as_columns:
        When ``True``, variable labels are used for DataFrame column names.
    variable_whitelist:
        Optional list of variable names to include.
    form_whitelist:
        Optional list of form IDs to include.

    Raises
    ------
    ImportError
        If the optional ``duckdb`` dependency is not installed.
    """
    try:
        import duckdb
    except ImportError as error:
        raise ImportError(
            "DuckDB export requires the optional 'duckdb' dependency. "
            "Install with `pip install 'imednet[duckdb]'`."
        ) from error

    df = _prepare_export_df(
        sdk,
        study_key,
        use_labels_as_columns=use_labels_as_columns,
        variable_whitelist=variable_whitelist,
        form_whitelist=form_whitelist,
    )

    conn: Any = duckdb.connect(db_path)
    try:
        conn.register(_DUCKDB_DF_ALIAS, df)
        conn.execute(
            f"CREATE OR REPLACE TABLE {_quote_duckdb_identifier(table_name)} "  # nosec B608
            f"AS SELECT * FROM {_quote_duckdb_identifier(_DUCKDB_DF_ALIAS)}"
        )
        conn.unregister(_DUCKDB_DF_ALIAS)
    finally:
        conn.close()


def export_to_duckdb_by_form(
    sdk: ImednetSDK,
    study_key: str,
    db_path: str,
    *,
    use_labels_as_columns: bool = False,
    variable_whitelist: Optional[List[str]] = None,
    form_whitelist: Optional[List[int]] = None,
) -> None:
    """Export records to separate DuckDB tables for each form.

    Each form is exported to a table named after ``form.form_key``.

    Parameters
    ----------
    sdk:
        Authenticated SDK instance used to fetch study records.
    study_key:
        Study identifier to export.
    db_path:
        Path to the target ``.duckdb`` database file.
    use_labels_as_columns:
        When ``True``, variable labels are used for DataFrame column names.
    variable_whitelist:
        Optional list of variable names to include.
    form_whitelist:
        Optional list of form IDs to include.

    Raises
    ------
    ImportError
        If the optional ``duckdb`` dependency is not installed.
    """
    try:
        import duckdb
    except ImportError as error:
        raise ImportError(
            "DuckDB export requires the optional 'duckdb' dependency. "
            "Install with `pip install 'imednet[duckdb]'`."
        ) from error

    conn: Any = duckdb.connect(db_path)
    try:
        for form in sdk.forms.list(study_key=study_key):
            if form.form_id is None or form.form_key is None:
                continue
            if form_whitelist is not None and form.form_id not in form_whitelist:
                continue

            df = _records_df(
                sdk,
                study_key,
                use_labels_as_columns=use_labels_as_columns,
                variable_whitelist=variable_whitelist,
                form_whitelist=[form.form_id],
            )
            df = _mask_df(df)

            conn.register(_DUCKDB_DF_ALIAS, df)
            conn.execute(
                f"CREATE OR REPLACE TABLE {_quote_duckdb_identifier(form.form_key)} "  # nosec B608
                f"AS SELECT * FROM {_quote_duckdb_identifier(_DUCKDB_DF_ALIAS)}"
            )
            conn.unregister(_DUCKDB_DF_ALIAS)
    finally:
        conn.close()


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
    """Export records to separate SQL tables for each form."""
    from sqlalchemy import create_engine

    mapper = _record_mapper()(sdk)
    engine = create_engine(conn_str)
    forms = sdk.forms.list(study_key=study_key)

    # Fetch all variables for the study once to avoid N+1 queries
    _form_filter: dict[str, Any] = {"formIds": form_whitelist} if form_whitelist else {}
    all_variables = sdk.variables.list(study_key=study_key, **_form_filter)
    variables_by_form: dict[int, list[Any]] = {}
    for v in all_variables:
        if v.form_id is not None:
            variables_by_form.setdefault(v.form_id, []).append(v)

    for form in forms:
        if form.form_id is None or form.form_key is None:
            continue
        if form_whitelist is not None and form.form_id not in form_whitelist:
            continue
        variables = variables_by_form.get(form.form_id, [])
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
                **({"variableNames": variable_whitelist} if variable_whitelist else {}),
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
            df = _mask_df(df)
        _to_sql_with_chunking(
            df,
            form.form_key or "",
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
    """Export records to a normalized long-format SQL table."""
    if pd is None:
        raise ImportError(
            (
                "pandas is required for export_to_long_sql. Install with "
                "'pip install pandas imednet-workflows'."
            )
        )
    from sqlalchemy import create_engine

    engine = create_engine(conn_str)
    mapper = _record_mapper()(sdk)
    records = mapper._fetch_records(study_key)

    rows: List[dict[str, Any]] = []
    first = True
    for rec in records:
        timestamp = rec.date_modified
        for name, value in (rec.record_data or {}).items():
            if global_sensitivity_registry.is_sensitive(name):
                masked_value = "***MASKED***"
            else:
                masked_value = mask_clinical_phi(value)

            rows.append(
                {
                    "record_id": rec.record_id,
                    "form_id": rec.form_id,
                    "variable_name": name,
                    "value": masked_value,
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
