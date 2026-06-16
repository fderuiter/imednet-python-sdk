from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Optional

import typer
from rich import print
from rich.markup import escape

from ...sdk import ImednetSDK
from ..decorators import with_sdk
from ..utils import STUDY_KEY_ARG, fetching_status

app = typer.Typer(name="export", help="Export study data to various formats.")

__all__ = ["app"]


@app.command("parquet")
@with_sdk
def export_parquet(
    sdk: ImednetSDK,
    study_key: str = STUDY_KEY_ARG,
    path: Path = typer.Argument(..., help="Destination Parquet file."),
) -> None:
    """Export study records to a Parquet file."""
    if importlib.util.find_spec("pyarrow") is None:
        print(
            "[bold red]Error:[/bold red] pyarrow is required for Parquet export. "
            "Install with 'pip install pyarrow imednet-workflows'."
        )
        raise typer.Exit(code=1)

    from .. import export_to_parquet

    with fetching_status("records for Parquet export", study_key):
        export_to_parquet(sdk, study_key, str(path))


@app.command("csv")
@with_sdk
def export_csv(
    sdk: ImednetSDK,
    study_key: str = STUDY_KEY_ARG,
    path: Path = typer.Argument(..., help="Destination CSV file."),
) -> None:
    """Export study records to a CSV file."""
    if importlib.util.find_spec("pandas") is None:
        print(
            "[bold red]Error:[/bold red] pandas is required for CSV export. "
            "Install with 'pip install pandas imednet-workflows'."
        )
        raise typer.Exit(code=1)

    from .. import export_to_csv

    with fetching_status("records for CSV export", study_key):
        export_to_csv(sdk, study_key, str(path))


@app.command("excel")
@with_sdk
def export_excel(
    sdk: ImednetSDK,
    study_key: str = STUDY_KEY_ARG,
    path: Path = typer.Argument(..., help="Destination Excel workbook."),
) -> None:
    """Export study records to an Excel workbook."""
    if importlib.util.find_spec("pandas") is None or importlib.util.find_spec("openpyxl") is None:
        print(
            "[bold red]Error:[/bold red] pandas and openpyxl are required for Excel export. "
            "Install with 'pip install pandas openpyxl imednet-workflows'."
        )
        raise typer.Exit(code=1)

    from .. import export_to_excel

    with fetching_status("records for Excel export", study_key):
        export_to_excel(sdk, study_key, str(path))


@app.command("json")
@with_sdk
def export_json_cmd(
    sdk: ImednetSDK,
    study_key: str = STUDY_KEY_ARG,
    path: Path = typer.Argument(..., help="Destination JSON file."),
) -> None:
    """Export study records to a JSON file."""
    from .. import export_to_json

    with fetching_status("records for JSON export", study_key):
        export_to_json(sdk, study_key, str(path))


@app.command("duckdb")
@with_sdk
def export_duckdb(
    sdk: ImednetSDK,
    study_key: str = STUDY_KEY_ARG,
    table_name: str = typer.Argument(..., help="Destination DuckDB table name."),
    db_path: Path = typer.Argument(..., help="Path to DuckDB database file."),
    vars_: str = typer.Option(
        None,
        "--vars",
        help="Comma-separated list of variable names to include.",
    ),
    forms: str = typer.Option(
        None,
        "--forms",
        help="Comma-separated list of form IDs to include.",
    ),
    use_labels: bool = typer.Option(
        False,
        "--use-labels",
        help="Use variable labels instead of names as column headers.",
    ),
) -> None:
    """Export study records to a DuckDB table."""
    if importlib.util.find_spec("duckdb") is None:
        print(
            "[bold red]Error:[/bold red] "
            + escape(
                "duckdb is required for DuckDB export. "
                "Install with \"pip install 'imednet[duckdb]'\"."
            )
        )
        raise typer.Exit(code=1)

    from .. import export_to_duckdb

    var_list = [v.strip() for v in vars_.split(",")] if vars_ else None
    form_list = [int(f.strip()) for f in forms.split(",")] if forms else None

    with fetching_status("records for DuckDB export", study_key):
        export_to_duckdb(
            sdk,
            study_key,
            str(db_path),
            table_name,
            use_labels_as_columns=use_labels,
            variable_whitelist=var_list,
            form_whitelist=form_list,
        )


@app.command("sql")
@with_sdk
def export_sql(
    sdk: ImednetSDK,
    study_key: str = STUDY_KEY_ARG,
    table: str = typer.Argument(
        ...,
        help=(
            "Destination table name. Ignored when exporting to SQLite unless "
            "--single-table is used."
        ),
    ),
    connection_string: str = typer.Argument(..., help="Database connection string."),
    single_table: bool = typer.Option(
        False,
        "--single-table",
        help="Store all records in a single table even when using SQLite.",
    ),
    long_format: bool = typer.Option(
        False,
        "--long-format",
        help="Export normalized long-format table.",
    ),
    vars_: str = typer.Option(
        None,
        "--vars",
        help="Comma-separated list of variable names to include.",
    ),
    forms: str = typer.Option(
        None,
        "--forms",
        help="Comma-separated list of form IDs to include.",
    ),
) -> None:
    """Export study records to a SQL table."""
    if importlib.util.find_spec("sqlalchemy") is None:
        print(
            "[bold red]Error:[/bold red] SQLAlchemy is required for SQL export. "
            "Install with 'pip install sqlalchemy imednet-workflows'."
        )
        raise typer.Exit(code=1)

    from sqlalchemy import create_engine

    from .. import export_to_long_sql, export_to_sql, export_to_sql_by_form

    engine = create_engine(connection_string)
    var_list = [v.strip() for v in vars_.split(",")] if vars_ else None
    form_list = [int(f.strip()) for f in forms.split(",")] if forms else None

    with fetching_status("records for SQL export", study_key):
        if long_format:
            export_to_long_sql(sdk, study_key, table, connection_string)
            return
        if not single_table and engine.dialect.name == "sqlite":
            export_to_sql_by_form(
                sdk,
                study_key,
                connection_string,
                variable_whitelist=var_list,
                form_whitelist=form_list,
            )
        else:
            export_to_sql(
                sdk,
                study_key,
                table,
                connection_string,
                variable_whitelist=var_list,
                form_whitelist=form_list,
            )


@app.command("mongodb")
@with_sdk
def export_mongodb(
    sdk: ImednetSDK,
    study_key: str = STUDY_KEY_ARG,
    uri: str = typer.Argument(..., help="MongoDB connection URI."),
    database: str = typer.Argument(..., help="MongoDB database name."),
    collection: str = typer.Argument(..., help="MongoDB collection name."),
    batch_size: int = typer.Option(500, "--batch-size", min=1, help="Records per batch."),
    upsert: bool = typer.Option(
        True,
        "--upsert/--insert-only",
        help="Use idempotent upserts (default) or insert-only mode.",
    ),
) -> None:
    """Export study records to MongoDB document envelopes."""
    if importlib.util.find_spec("pymongo") is None:
        print(
            "[bold red]Error:[/bold red] "
            + escape(
                "pymongo is required for MongoDB export. "
                "Install with \"pip install 'imednet[mongodb]'\"."
            )
        )
        raise typer.Exit(code=1)

    from imednet.integrations import SinkConfig

    if sdk.sinks is None:
        print("[bold red]Error:[/bold red] imednet-plugins-sinks is required.")
        raise typer.Exit(code=1)

    cfg = SinkConfig(batch_size=batch_size, idempotent=upsert)
    with fetching_status("records for MongoDB export", study_key):
        sdk.sinks.export_to_mongodb(
            sdk,
            study_key,
            uri,
            database,
            collection,
            config=cfg,
        )


@app.command("neo4j")
@with_sdk
def export_neo4j(
    sdk: ImednetSDK,
    study_key: str = STUDY_KEY_ARG,
    uri: str = typer.Argument(..., help="Neo4j URI (bolt:// or neo4j+s://)."),
    username: str = typer.Argument(..., help="Neo4j username."),
    password: str = typer.Argument(..., help="Neo4j password."),
    database: str = typer.Option("neo4j", "--database", help="Neo4j database name."),
    batch_size: int = typer.Option(500, "--batch-size", min=1, help="Records per batch."),
    merge: bool = typer.Option(
        True,
        "--merge/--create-only",
        help="Use idempotent MERGE semantics (default) or CREATE-only writes.",
    ),
) -> None:
    """Export study records to Neo4j nodes and relationships."""
    if importlib.util.find_spec("neo4j") is None:
        print(
            "[bold red]Error:[/bold red] "
            + escape(
                "neo4j is required for Neo4j export. Install with \"pip install 'imednet[neo4j]'\"."
            )
        )
        raise typer.Exit(code=1)

    if sdk.sinks is None:
        print("[bold red]Error:[/bold red] imednet-plugins-sinks is required.")
        raise typer.Exit(code=1)

    cfg = sdk.sinks.Neo4jSinkConfig(batch_size=batch_size, idempotent=merge, database=database)
    with fetching_status("records for Neo4j export", study_key):
        sdk.sinks.export_to_neo4j(
            sdk,
            study_key,
            uri,
            (username, password),
            config=cfg,
        )


@app.command("snowflake")
@with_sdk
def export_snowflake(
    sdk: ImednetSDK,
    study_key: str = STUDY_KEY_ARG,
    account: str = typer.Argument(..., help="Snowflake account identifier."),
    user: str = typer.Argument(..., help="Snowflake username."),
    password: str = typer.Argument(..., help="Snowflake password."),
    database: str = typer.Argument(..., help="Target Snowflake database."),
    schema: str = typer.Argument(..., help="Target Snowflake schema."),
    warehouse: str = typer.Argument(..., help="Snowflake warehouse."),
    stage: str = typer.Argument(..., help="Internal stage name."),
    table: str = typer.Argument(..., help="Target table name."),
    stage_prefix: str = typer.Option("imednet", "--stage-prefix", help="Path prefix in stage."),
    local_staging_dir: Optional[Path] = typer.Option(
        None, "--local-staging-dir", help="Local directory for staged Parquet files."
    ),
    manifest_path: Optional[Path] = typer.Option(
        None, "--manifest-path", help="Optional JSONL manifest output path."
    ),
    batch_size: int = typer.Option(500, "--batch-size", min=1, help="Records per batch."),
    idempotent: bool = typer.Option(
        True,
        "--idempotent/--force-reload",
        help="Skip already-loaded files (default) or force reloading.",
    ),
) -> None:
    """Export study records to Snowflake using staged Parquet + COPY INTO."""
    if importlib.util.find_spec("snowflake.connector") is None:
        print(
            "[bold red]Error:[/bold red] "
            + escape(
                "snowflake-connector-python is required for Snowflake export. "
                "Install with \"pip install 'imednet[snowflake]'\"."
            )
        )
        raise typer.Exit(code=1)
    if importlib.util.find_spec("pyarrow") is None:
        print(
            "[bold red]Error:[/bold red] "
            + escape(
                "pyarrow is required for Snowflake export. "
                "Install with \"pip install 'imednet[snowflake]'\"."
            )
        )
        raise typer.Exit(code=1)

    if sdk.sinks is None:
        print("[bold red]Error:[/bold red] imednet-plugins-sinks is required.")
        raise typer.Exit(code=1)

    cfg = sdk.sinks.SnowflakeSinkConfig(
        account=account,
        user=user,
        password=password,
        database=database,
        schema=schema,
        warehouse=warehouse,
        stage=stage,
        table=table,
        stage_prefix=stage_prefix,
        local_staging_dir=local_staging_dir,
        manifest_path=manifest_path,
        batch_size=batch_size,
        idempotent=idempotent,
    )
    with fetching_status("records for Snowflake export", study_key):
        sdk.sinks.export_to_snowflake(
            sdk,
            study_key,
            config=cfg,
        )
