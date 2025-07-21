from __future__ import annotations

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
from ..workflows.data_extraction import DataExtractionWorkflow  # noqa: F401
from ..workflows.subject_data import SubjectDataWorkflow  # noqa: F401
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
from .jobs import app as jobs_app  # noqa: E402
from .queries import app as queries_app  # noqa: E402
from .record_revisions import app as record_revisions_app  # noqa: E402
from .records import app as records_app  # noqa: E402
from .sites import app as sites_app  # noqa: E402
from .studies import app as studies_app  # noqa: E402
from .subject_data import subject_data  # noqa: E402
from .subjects import app as subjects_app  # noqa: E402
from .variables import app as variables_app  # noqa: E402
from .workflows import app as workflows_app  # noqa: E402

app.add_typer(studies_app)
app.add_typer(queries_app)
app.add_typer(variables_app)
app.add_typer(record_revisions_app)
app.add_typer(sites_app)
app.add_typer(export_app)
app.add_typer(subjects_app)
app.add_typer(jobs_app)
app.add_typer(records_app)
app.add_typer(workflows_app)
app.command("subject-data")(subject_data)

if __name__ == "__main__":  # pragma: no cover - manual invocation
    app()
