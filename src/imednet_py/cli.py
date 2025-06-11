"""Command line interface for iMednet SDK."""

import typer


app = typer.Typer()


@app.callback()
def main() -> None:
    """iMednet command line interface."""
    pass


@app.command()
def version() -> None:
    """Print package version."""
    from . import __version__

    typer.echo(__version__)


if __name__ == "__main__":
    app()
