import typer
import pandas as pd
from pathlib import Path
from rich.console import Console

from imednet.sdk import ImednetSDK
from .decorators import with_sdk
from imednet.tlf.definitions import TLF_DEFINITIONS

app = typer.Typer(help="Generate Tables, Listings, and Figures (TLFs).")


@app.command()
@with_sdk
def generate(
    sdk: ImednetSDK,
    tlf_name: str = typer.Argument(..., help="The name of the TLF to generate."),
    study_id: str = typer.Argument(..., help="The ID of the study."),
    output_path: Path = typer.Option(None, "--out", "-o", help="Output file path for CSV. If not provided, prints to console."),
):
    """
    Generate a TLF for a given study.
    """
    console = Console()
    console.print(f"Generating TLF '{tlf_name}' for study '{study_id}'...")

    tlf_class = TLF_DEFINITIONS.get(tlf_name)
    if not tlf_class:
        console.print(f"[bold red]Error:[/bold red] Unknown TLF: '{tlf_name}'")
        raise typer.Exit(code=1)

    definition = tlf_class()

    try:
        df = definition.generate(sdk, study_id)
    except Exception as e:
        console.print(f"[bold red]Error generating data:[/bold red] {e}")
        raise typer.Exit(code=1)

    if df.empty:
        console.print("[yellow]Warning:[/yellow] No data returned for this TLF.")
        return

    if output_path:
        if output_path.suffix.lower() != ".csv":
            console.print("[bold red]Error:[/bold red] Output path must have a .csv extension.")
            raise typer.Exit(code=1)

        try:
            df.to_csv(output_path, index=False)
            console.print(f"Output successfully saved to [cyan]{output_path}[/cyan]")
        except Exception as e:
            console.print(f"[bold red]Error saving file:[/bold red] {e}")
            raise typer.Exit(code=1)
    else:
        console.print(df.to_string())

    console.print("[green]Done.[/green]")
