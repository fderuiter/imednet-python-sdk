from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Optional

import typer
from rich import print

from ...sdk import ImednetSDK
from ..decorators import with_sdk
from ..utils import STUDY_KEY_ARG, display_list, fetching_status

app = typer.Typer(name="records", help="Manage records within a study.")


@app.command("list")
@with_sdk
def list_records(
    sdk: ImednetSDK,
    study_key: str = STUDY_KEY_ARG,
    output: Optional[str] = typer.Option(
        None,
        "--output",
        "-o",
        help="Save records to the given format",
        show_choices=True,
        rich_help_panel="Output Options",
    ),
) -> None:
    """List records for a study."""
    if output and output.lower() not in {"json", "csv"}:
        print("[bold red]Invalid output format. Use 'json' or 'csv'.[/bold red]")
        raise typer.Exit(code=1)

    with fetching_status("records", study_key):
        records = sdk.records.list(study_key)

    if output:
        path = Path(f"records.{output}")
        # Export full data
        data = [r.model_dump(by_alias=True) for r in records]

        if output == "csv":
            if data:
                # Sanitize data to prevent CSV injection
                for row in data:
                    for k, v in row.items():
                        if isinstance(v, str) and v.startswith(("=", "+", "-", "@")):
                            row[k] = f"'{v}"

                keys = data[0].keys()
                with open(path, "w", newline="", encoding="utf-8") as f:
                    writer = csv.DictWriter(f, fieldnames=keys)
                    writer.writeheader()
                    writer.writerows(data)
            else:
                # Create empty file
                path.touch()
        else:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, default=str)

        print(f"Saved {len(records)} records to {path}")
    else:
        # Display simplified view
        view_models = []
        for r in records:
            view_models.append(
                {
                    "ID": r.record_id,
                    "Subject": r.subject_key,
                    "Form": r.form_key,
                    "Status": r.record_status,
                    "Created": r.date_created,
                }
            )

        display_list(view_models, "records", "No records found.")
