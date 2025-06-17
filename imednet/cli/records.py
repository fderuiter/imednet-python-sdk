from __future__ import annotations

from pathlib import Path
from typing import Optional

import pandas as pd
import typer
from rich import print

from ..core.exceptions import ApiError

app = typer.Typer(name="records", help="Manage records within a study.")


@app.command("list")
def list_records(
    study_key: str = typer.Argument(..., help="The key identifying the study."),
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
    from . import get_sdk

    sdk = get_sdk()
    try:
        if output and output.lower() not in {"json", "csv"}:
            print("[bold red]Invalid output format. Use 'json' or 'csv'.[/bold red]")
            raise typer.Exit(code=1)
        print(f"Fetching records for study '{study_key}'...")
        records = sdk.records.list(study_key)
        rows = [r.model_dump(by_alias=True) for r in records]
        df = pd.DataFrame(rows)

        if output:
            path = Path(f"records.{output}")
            if output == "csv":
                df.to_csv(path, index=False)
            else:
                df.to_json(path, orient="records", indent=2)
            print(f"Saved {len(df)} records to {path}")
        else:
            if df.empty:
                print("No records found.")
            else:
                print(df.head().to_string(index=False))
                if len(df) > 5:
                    print(f"... ({len(df)} total records)")
    except ApiError as exc:
        print(f"[bold red]API Error:[/bold red] {exc}")
        raise typer.Exit(code=1)
    except Exception as exc:  # pragma: no cover - defensive
        print(f"[bold red]An unexpected error occurred:[/bold red] {exc}")
        raise typer.Exit(code=1)
