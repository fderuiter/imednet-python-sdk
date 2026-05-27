Export Destinations
===================

This guide explains when to use each export destination family and how to install
only the optional dependencies you need.

For sink internals and data-flow architecture, see :doc:`architecture`.
For full CLI syntax, see :doc:`cli`.

Installation
------------

.. code-block:: bash

   # Core tabular stack (CSV/Excel/JSON/SQL/DuckDB/Parquet)
   pip install "imednet[export]"

   # Destination-specific extras for structure-preserving / warehouse exports
   pip install "imednet[mongodb]"
   pip install "imednet[neo4j]"
   pip install "imednet[snowflake]"

   # Multiple destinations in one install
   pip install "imednet[mongodb,neo4j,snowflake]"

Destination decision matrix
---------------------------

.. list-table::
   :header-rows: 1
   :widths: 18 26 28 28

   * - Destination
     - Best fit
     - Data-shape characteristics
     - Operational constraints
   * - MongoDB
     - Application-facing document reads, schema-preserving archival
     - Keeps nested ``record_data`` as document fields and stores record metadata
       envelope fields (study/form/visit/subject)
     - Requires ``pymongo`` and a MongoDB URI. Graph traversal and relationship
       analytics are weaker than a native graph store.
   * - Neo4j
     - Relationship-heavy exploration and lineage queries
     - Preserves the hierarchy ``Study → Subject → Visit → Record`` as nodes and
       relationships, with ``record_data`` attached to ``Record`` nodes
     - Requires ``neo4j`` driver and Bolt/Neo4j endpoint credentials.
       Idempotent mode uses ``MERGE`` for safe re-runs.
   * - Snowflake
     - Warehouse-native analytics and bulk loading at scale
     - Writes Parquet batch files, uploads to an internal stage, then issues
       ``COPY INTO`` for table loading
     - Requires ``snowflake-connector-python`` + ``pyarrow`` and stage privileges
       for ``PUT`` / ``COPY INTO``.

SDK examples
------------

MongoDB (document export):

.. code-block:: python

   from imednet import ImednetSDK
   from imednet.integrations import SinkConfig, export_to_mongodb

   sdk = ImednetSDK(...)
   rows = export_to_mongodb(
       sdk,
       "MY_STUDY",
       "mongodb://localhost:27017",
       "imednet",
       "records",
       config=SinkConfig(batch_size=500, idempotent=True),
   )
   print(rows)

Neo4j (graph export):

.. code-block:: python

   from imednet import ImednetSDK
   from imednet.integrations import Neo4jSinkConfig, export_to_neo4j

   sdk = ImednetSDK(...)
   rows = export_to_neo4j(
       sdk,
       "MY_STUDY",
       "bolt://localhost:7687",
       ("neo4j", "..."),
       config=Neo4jSinkConfig(database="neo4j", batch_size=500, idempotent=True),
   )
   print(rows)

Snowflake (warehouse-native export):

.. code-block:: python

   from imednet import ImednetSDK
   from imednet.integrations import SnowflakeSinkConfig, export_to_snowflake

   sdk = ImednetSDK(...)
   cfg = SnowflakeSinkConfig(
       account="myorg-myaccount",
       user="loader",
       **{"password": "..."},
       database="IMEDNET_DB",
       schema="PUBLIC",
       warehouse="COMPUTE_WH",
       stage="MY_STAGE",
       table="RECORDS",
   )
   rows = export_to_snowflake(sdk, "MY_STUDY", config=cfg)
   print(rows)

Runnable examples
-----------------

* :doc:`examples/mongodb_export`
* :doc:`examples/neo4j_export`
* :doc:`examples/snowflake_export`
