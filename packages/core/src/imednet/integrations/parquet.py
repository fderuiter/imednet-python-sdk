"""Hive-partitioned Parquet integration helpers."""

from __future__ import annotations

from importlib import import_module
from pathlib import Path
from typing import Any, List, Optional

from ..sdk import ImednetSDK
from ..utils import validate_partition_key
from .export import _record_mapper


def _ensure_pyarrow() -> None:
    try:
        import_module("pyarrow")
    except ImportError as error:
        raise ImportError(
            "PyArrow is required for Hive Parquet export. Install with "
            "\"pip install 'imednet[export]'\"."
        ) from error


def export_to_hive_parquet(
    sdk: ImednetSDK,
    study_key: str,
    base_dir: str,
    *,
    use_labels_as_columns: bool = False,
    variable_whitelist: Optional[List[str]] = None,
    form_whitelist: Optional[List[int]] = None,
) -> None:
    """Export study records to a Hive-partitioned Parquet directory layout."""
    _ensure_pyarrow()
    validate_partition_key(study_key)

    mapper = _record_mapper()(sdk)
    forms = sdk.forms.list(study_key=study_key)

    form_filter: dict[str, Any] = {"formIds": form_whitelist} if form_whitelist else {}
    all_variables = sdk.variables.list(study_key=study_key, **form_filter)
    variables_by_form: dict[int, list[Any]] = {}
    for variable in all_variables:
        variables_by_form.setdefault(variable.form_id, []).append(variable)

    study_dir = Path(base_dir) / f"study_key={study_key}"
    for form in forms:
        if form_whitelist is not None and form.form_id not in form_whitelist:
            continue

        variables = variables_by_form.get(form.form_id, [])
        variable_keys = [
            variable.variable_name
            for variable in variables
            if variable_whitelist is None or variable.variable_name in variable_whitelist
        ]
        label_map = {
            variable.variable_name: variable.label
            for variable in variables
            if variable.variable_name in variable_keys
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

        validate_partition_key(form.form_key)
        output_dir = study_dir / f"form_key={form.form_key}"
        output_dir.mkdir(parents=True, exist_ok=True)
        df.to_parquet(output_dir / "records.parquet", index=False, engine="pyarrow")


def hive_parquet_query(base_dir: str) -> str:
    """Return the DuckDB read_parquet query string for the given Hive base directory."""
    escaped_base_dir = base_dir.replace("'", "''")
    return (
        f"SELECT * FROM read_parquet('{escaped_base_dir}/**/*.parquet', "
        "hive_partitioning = true)"
    )


__all__ = ["export_to_hive_parquet", "hive_parquet_query"]
