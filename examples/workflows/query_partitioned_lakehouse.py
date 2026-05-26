"""Example showing safe analytical reads from a partitioned Hive Parquet lakehouse."""

from __future__ import annotations

import os

import duckdb

from imednet.integrations.parquet import hive_parquet_query

base_dir = os.getenv("IMEDNET_LAKEHOUSE_DIR", "/tmp/lakehouse")

query = (
    "SELECT study_key, form_key, COUNT(*) AS row_count "
    f"FROM ({hive_parquet_query(base_dir)}) records "
    "GROUP BY study_key, form_key "
    "ORDER BY study_key, form_key"
)

rows = duckdb.connect(":memory:").execute(query).fetchall()
for row in rows:
    print(row)
