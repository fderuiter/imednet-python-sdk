from __future__ import annotations

import importlib.util
from pathlib import Path

import typer
from rich import print

from ...sdk import ImednetSDK
from ..decorators import with_sdk
from ..utils import STUDY_KEY_ARG

app = typer.Typer(name="export", help="Export study data to various formats.")


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
            "Install with 'pip install \"imednet[pyarrow]\"'."
        )
        raise typer.Exit(code=1)

    from .. import export_to_parquet

    export_to_parquet(sdk, study_key, str(path))


@app.command("csv")
@with_sdk
def export_csv(
    sdk: ImednetSDK,
    study_key: str = STUDY_KEY_ARG,
    path: Path = typer.Argument(..., help="Destination CSV file."),
) -> None:
    """Export study records to a CSV file."""
    from .. import export_to_csv

    export_to_csv(sdk, study_key, str(path))


@app.command("excel")
@with_sdk
def export_excel(
    sdk: ImednetSDK,
    study_key: str = STUDY_KEY_ARG,
    path: Path = typer.Argument(..., help="Destination Excel workbook."),
) -> None:
    """Export study records to an Excel workbook."""
    from .. import export_to_excel

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

    export_to_json(sdk, study_key, str(path))


@app.command("sql")
@with_sdk
def export_sql(
    sdk: ImednetSDK,
    study_key: str = STUDY_KEY_ARG,
    table: str = typer.Argument(..., help="Destination table name."),
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
            "Install with 'pip install \"imednet[sqlalchemy]\"'."
        )
        raise typer.Exit(code=1)

    from sqlalchemy import create_engine

    from .. import export_to_long_sql, export_to_sql, export_to_sql_by_form

    engine = create_engine(connection_string)
    var_list = [v.strip() for v in vars_.split(",")] if vars_ else None
    form_list = [int(f.strip()) for f in forms.split(",")] if forms else None
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
