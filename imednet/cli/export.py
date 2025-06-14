from __future__ import annotations

import importlib.util
from pathlib import Path

import typer
from rich import print

app = typer.Typer(name="export", help="Export study data to various formats.")


@app.command("parquet")
def export_parquet(
    study_key: str = typer.Argument(..., help="The key identifying the study."),
    path: Path = typer.Argument(..., help="Destination Parquet file."),
) -> None:
    """Export study records to a Parquet file."""
    if importlib.util.find_spec("pyarrow") is None:
        print(
            "[bold red]Error:[/bold red] pyarrow is required for Parquet export. "
            "Install with 'pip install \"imednet-sdk[pyarrow]\"'."
        )
        raise typer.Exit(code=1)

    from . import export_to_parquet, get_sdk

    sdk = get_sdk()
    try:
        export_to_parquet(sdk, study_key, str(path))
    except Exception as exc:
        print(f"[bold red]Error:[/bold red] {exc}")
        raise typer.Exit(code=1)


@app.command("csv")
def export_csv(
    study_key: str = typer.Argument(..., help="The key identifying the study."),
    path: Path = typer.Argument(..., help="Destination CSV file."),
) -> None:
    """Export study records to a CSV file."""
    from . import export_to_csv, get_sdk

    sdk = get_sdk()
    try:
        export_to_csv(sdk, study_key, str(path))
    except Exception as exc:
        print(f"[bold red]Error:[/bold red] {exc}")
        raise typer.Exit(code=1)


@app.command("excel")
def export_excel(
    study_key: str = typer.Argument(..., help="The key identifying the study."),
    path: Path = typer.Argument(..., help="Destination Excel workbook."),
) -> None:
    """Export study records to an Excel workbook."""
    from . import export_to_excel, get_sdk

    sdk = get_sdk()
    try:
        export_to_excel(sdk, study_key, str(path))
    except Exception as exc:
        print(f"[bold red]Error:[/bold red] {exc}")
        raise typer.Exit(code=1)


@app.command("json")
def export_json_cmd(
    study_key: str = typer.Argument(..., help="The key identifying the study."),
    path: Path = typer.Argument(..., help="Destination JSON file."),
) -> None:
    """Export study records to a JSON file."""
    from . import export_to_json, get_sdk

    sdk = get_sdk()
    try:
        export_to_json(sdk, study_key, str(path))
    except Exception as exc:
        print(f"[bold red]Error:[/bold red] {exc}")
        raise typer.Exit(code=1)


@app.command("sql")
def export_sql(
    study_key: str = typer.Argument(..., help="The key identifying the study."),
    table: str = typer.Argument(..., help="Destination table name."),
    connection_string: str = typer.Argument(..., help="Database connection string."),
) -> None:
    """Export study records to a SQL table."""
    if importlib.util.find_spec("sqlalchemy") is None:
        print(
            "[bold red]Error:[/bold red] SQLAlchemy is required for SQL export. "
            "Install with 'pip install \"imednet-sdk[sqlalchemy]\"'."
        )
        raise typer.Exit(code=1)

    from . import export_to_sql, get_sdk

    sdk = get_sdk()
    try:
        export_to_sql(sdk, study_key, table, connection_string)
    except Exception as exc:
        print(f"[bold red]Error:[/bold red] {exc}")
        raise typer.Exit(code=1)
