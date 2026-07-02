Query partitioned lakehouse
===========================

Use DuckDB with ``hive_partitioning=true`` and ``union_by_name=true`` so mixed-schema Parquet batches remain queryable.

.. literalinclude:: /../examples/workflows/query_partitioned_lakehouse.py
   :language: python
