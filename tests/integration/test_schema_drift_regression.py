"""Regression tests for schema-drift / analytical-read compatibility.

These tests ensure that historical Parquet datasets with evolved schemas
remain queryable and that DuckDB integration handles schema changes gracefully.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import duckdb
import pandas as pd
import pytest

from imednet.integrations.parquet import export_to_hive_parquet, hive_parquet_query
from imednet.integrations.parquet_engine import PyArrowDatasetPartitionedStorageEngine


def test_mixed_schema_parquet_queryable(tmp_path: Path) -> None:
    """Verify that partitions with different columns can be read together."""
    import pyarrow as pa

    engine = PyArrowDatasetPartitionedStorageEngine()
    base_dir = tmp_path / "dataset"
    base_dir.mkdir()

    # Batch 1: Columns A, B
    df1 = pd.DataFrame({"record_id": [1], "A": [10], "B": ["x"]})
    table1 = pa.Table.from_pandas(df1, preserve_index=False)
    engine.write_form_table(table1, base_dir=str(base_dir), study_key="S", form_key="F")

    # Batch 2: Columns A, C (B missing, C added)
    df2 = pd.DataFrame({"record_id": [2], "A": [20], "C": [True]})
    table2 = pa.Table.from_pandas(df2, preserve_index=False)
    engine.write_form_table(table2, base_dir=str(base_dir), study_key="S", form_key="F")

    # Query via DuckDB helper
    query = hive_parquet_query(str(base_dir))
    df_result = duckdb.query(query).to_df()

    assert len(df_result) == 2
    assert "B" in df_result.columns
    assert "C" in df_result.columns

    # Verify values and null handling
    row1 = df_result[df_result["record_id"] == 1].iloc[0]
    assert row1["A"] == 10
    assert row1["B"] == "x"
    assert pd.isna(row1["C"])

    row2 = df_result[df_result["record_id"] == 2].iloc[0]
    assert row2["A"] == 20
    assert pd.isna(row2["B"])
    assert bool(row2["C"]) is True


def test_union_by_name_preserves_data_integrity(tmp_path: Path) -> None:
    """Verify that columns are matched by name even if order differs."""
    import pyarrow as pa

    engine = PyArrowDatasetPartitionedStorageEngine()
    base_dir = tmp_path / "union_dataset"
    base_dir.mkdir()

    # Batch 1: A, B
    df1 = pd.DataFrame({"record_id": [1], "A": [1], "B": [2]})
    table1 = pa.Table.from_pandas(df1, preserve_index=False)
    engine.write_form_table(table1, base_dir=str(base_dir), study_key="S", form_key="F")

    # Batch 2: B, A (reversed order)
    df2 = pd.DataFrame({"record_id": [2], "B": [4], "A": [3]})
    table2 = pa.Table.from_pandas(df2, preserve_index=False)
    engine.write_form_table(table2, base_dir=str(base_dir), study_key="S", form_key="F")

    query = hive_parquet_query(str(base_dir))
    df_result = duckdb.query(query).to_df()

    assert len(df_result) == 2
    assert df_result[df_result["record_id"] == 1]["A"].iloc[0] == 1
    assert df_result[df_result["record_id"] == 1]["B"].iloc[0] == 2
    assert df_result[df_result["record_id"] == 2]["A"].iloc[0] == 3
    assert df_result[df_result["record_id"] == 2]["B"].iloc[0] == 4


def test_order_independent_reads(tmp_path: Path) -> None:
    """Verify that analytical reads do not depend on column order."""
    # This is partially covered by union_by_name, but specifically check
    # that selecting specific columns works regardless of batch order.
    import pyarrow as pa

    engine = PyArrowDatasetPartitionedStorageEngine()
    base_dir = tmp_path / "order_dataset"
    base_dir.mkdir()

    pa.Table.from_pandas(pd.DataFrame({"A": [1], "B": [2]}), preserve_index=False)
    engine.write_form_table(
        pa.Table.from_pandas(pd.DataFrame({"A": [1], "B": [2]}), preserve_index=False),
        base_dir=str(base_dir),
        study_key="S",
        form_key="F",
    )

    engine.write_form_table(
        pa.Table.from_pandas(pd.DataFrame({"B": [4], "A": [3]}), preserve_index=False),
        base_dir=str(base_dir),
        study_key="S",
        form_key="F",
    )

    # Select specific order
    query = f"SELECT B, A FROM read_parquet('{base_dir}/**/*.parquet', hive_partitioning=True, union_by_name=True)"
    df_result = duckdb.query(query).to_df()

    assert df_result.columns.tolist()[:2] == ["B", "A"]
    assert set(df_result["A"]) == {1, 3}
    assert set(df_result["B"]) == {2, 4}


def test_helper_query_generation_alignment() -> None:
    """Verify hive_parquet_query produces the intended compatible query string."""
    query = hive_parquet_query("/tmp/data")
    assert "read_parquet" in query
    assert "hive_partitioning = true" in query
    assert "union_by_name = true" in query
    assert "/tmp/data/**/*.parquet" in query

    # Test escaping
    query_escaped = hive_parquet_query("/tmp/o'hara")
    assert "/tmp/o''hara" in query_escaped
