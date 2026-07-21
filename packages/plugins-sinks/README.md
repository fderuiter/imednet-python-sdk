# imednet-plugins-sinks

Unified database sinks plugin for the iMednet Python SDK.

## Install

Install the package via standard pip using the public package distribution name:

```bash
pip install imednet-plugins-sinks
```

Or using the workspace-relative path install command:

```bash
pip install ./packages/plugins-sinks
```

**Optional Dependencies:**
Depending on your target backend, you can install the required drivers using optional dependency flags:
- MongoDB: `pip install imednet-plugins-sinks[mongodb]`
- Neo4j: `pip install imednet-plugins-sinks[neo4j]`
- Snowflake: `pip install imednet-plugins-sinks[snowflake]`
- All Sinks: `pip install imednet-plugins-sinks[all]`

## Launch via CLI

The package provides a unified SDK namespace integration (`SinksNamespace`) directly registered with the core SDK client via entry points (`imednet.plugins`).

You can initialize and execute sinks programmatically:

```python
from imednet_sinks import export_to_mongodb, export_to_neo4j, export_to_snowflake

# Example module runner command to execute an export
# export_to_mongodb(
#     study_key='STUDY-123',
#     connection_uri='mongodb://localhost:27017',
#     database='imednet'
# )
```

Alternatively, commands can be launched via standard CLI structures mapped to these functions if exposed by your main SDK runner.

## Features

- **Multi-backend Support**: Tailored exporters mapping data to Document Store (MongoDB), Property Graph (Neo4j), or Data Warehouse (Snowflake) systems.
- **Dynamic Lazy Imports**: Keeps package initialization light by lazy-loading heavy drivers (e.g. PyMongo, Neo4j, PyArrow) at execution time.
- **Idempotency & Resiliency**: 
  - **MongoDB**: Uses bulk upserts mapping unique compound keys (`<study_key>/<record_id>`) using PyMongo `bulk_write` update/upsert actions.
  - **Neo4j**: Merges hierarchies (`Study -> Subject -> Visit -> Record`) idempotently using query templates.
  - **Snowflake**: Two-phase loading converting records to Apache Arrow tables, writing Parquet stages, and running atomic transactional `COPY INTO` with `FORCE = FALSE`.
- **Unified SDK Namespace Integration**: Seamless integration through the `SinksNamespace` registered directly with the core SDK client.

## Component Description Table

| Component | Description |
|-----------|-------------|
| `MongoDbExportSink` | Document store backend exporter using PyMongo `bulk_write` and upserts. |
| `Neo4jExportSink` | Property graph backend exporter merging hierarchical models idempotently. |
| `SnowflakeExportSink` | Data warehouse backend exporter using Apache Arrow and atomic `COPY INTO`. |
| `SinksNamespace` | Unified SDK namespace integration registered with the core SDK client. |
