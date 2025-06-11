"""Command line interface for iMednet SDK."""
import click

@click.group()
def cli() -> None:
    """iMednet command line interface."""

@cli.command()
def version() -> None:
    """Print package version."""
    from . import __version__
    click.echo(__version__)

if __name__ == "__main__":
    cli()
