from __future__ import annotations

from importlib import import_module

import typer
from dotenv import load_dotenv

# Re-export for tests
from ..integrations.export import export_to_csv  # noqa: F401
from ..integrations.export import export_to_excel  # noqa: F401
from ..integrations.export import export_to_json  # noqa: F401
from ..integrations.export import export_to_long_sql  # noqa: F401
from ..integrations.export import export_to_parquet  # noqa: F401
from ..integrations.export import export_to_sql  # noqa: F401
from ..integrations.export import export_to_sql_by_form  # noqa: F401
from .decorators import with_sdk  # noqa: F401
from .utils import get_sdk, parse_filter_args  # noqa: F401

# ruff: noqa: I001


load_dotenv()

app = typer.Typer(help="iMednet SDK Command Line Interface")


@app.callback()
def main(ctx: typer.Context) -> None:  # pragma: no cover - simple passthrough
    """iMednet SDK CLI entry point."""
    pass


# Subcommands
from .export import app as export_app  # noqa: E402
from .intervals import app as intervals_app  # noqa: E402
from .jobs import app as jobs_app  # noqa: E402
from .queries import app as queries_app  # noqa: E402
from .record_revisions import app as record_revisions_app  # noqa: E402
from .records import app as records_app  # noqa: E402
from .sites import app as sites_app  # noqa: E402
from .studies import app as studies_app  # noqa: E402
from .subjects import app as subjects_app  # noqa: E402
from .variables import app as variables_app  # noqa: E402

app.add_typer(studies_app)
app.add_typer(queries_app)
app.add_typer(variables_app)
app.add_typer(record_revisions_app)
app.add_typer(sites_app)
app.add_typer(export_app)
app.add_typer(subjects_app)
app.add_typer(intervals_app)
app.add_typer(jobs_app)
app.add_typer(records_app)


def _register_missing_workflow_commands() -> None:
    workflows_app = typer.Typer(
        name="workflows",
        help="Execute opinionated business logic (requires imednet-workflows).",
    )

    def _missing_plugin() -> None:
        typer.secho(
            "The workflows plugin is not installed. Run: pip install imednet-workflows",
            fg=typer.colors.RED,
        )
        raise typer.Exit(code=1)

    @workflows_app.command("extract-records")
    def missing_extract_records() -> None:
        """Execute opinionated business logic (missing plugin)."""
        _missing_plugin()

    @app.command("subject-data")
    def missing_subject_data() -> None:
        """Retrieve all data for a single subject (missing plugin)."""
        _missing_plugin()

    app.add_typer(workflows_app)


try:  # pragma: no cover - optional workflows plugin
    workflows_cli = import_module("imednet_workflows.cli")
    DataExtractionWorkflow = import_module(  # noqa: F401
        "imednet_workflows.data_extraction"
    ).DataExtractionWorkflow
    SubjectDataWorkflow = import_module(
        "imednet_workflows.subject_data"
    ).SubjectDataWorkflow  # noqa: F401
    app.add_typer(workflows_cli.app)
    app.command("subject-data")(workflows_cli.subject_data)
except (ImportError, ModuleNotFoundError, AttributeError):  # pragma: no cover - optional plugin
    DataExtractionWorkflow = None  # type: ignore[assignment]
    SubjectDataWorkflow = None  # type: ignore[assignment]
    _register_missing_workflow_commands()


@app.command(hidden=True)
def tui(ctx: typer.Context) -> None:
    """Launch the interactive terminal user interface (Dashboard)."""
    typer.echo("TUI mode has been removed. Please use the CLI commands.")
    raise typer.Exit(code=1)


if __name__ == "__main__":  # pragma: no cover - manual invocation
    app()
