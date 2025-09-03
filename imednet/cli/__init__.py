from __future__ import annotations

from typing import Optional

import typer
from dotenv import load_dotenv

from .. import __version__
from . import (
    export,
    jobs,
    queries,
    record_revisions,
    records,
    sites,
    studies,
    subject_data,
    subjects,
    testing,
    variables,
    workflows,
)

load_dotenv()


def version_callback(value: bool) -> None:
    if value:
        print(f"iMednet SDK version: {__version__}")
        raise typer.Exit()


app = typer.Typer(
    name="imednet",
    help="iMednet CLI",
    add_completion=False,
    no_args_is_help=True,
)


@app.callback()
def cli(
    version: Optional[bool] = typer.Option(
        None,
        "--version",
        callback=version_callback,
        is_eager=True,
        help="Show the application's version and exit.",
    )
) -> None: ...


app.add_typer(studies.app)
app.add_typer(queries.app)
app.add_typer(variables.app)
app.add_typer(record_revisions.app)
app.add_typer(sites.app)
app.add_typer(export.app)
app.add_typer(subjects.app)
app.add_typer(jobs.app)
app.add_typer(records.app)
app.add_typer(workflows.app)
app.add_typer(testing.app, name="testing")
app.command("subject-data")(subject_data.subject_data)

if __name__ == "__main__":  # pragma: no cover - manual invocation
    app()
