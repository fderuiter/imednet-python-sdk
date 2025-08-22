import typer
from typing_extensions import Annotated

from imednet.sdk import ImednetSDK
from imednet.cli.decorators import with_sdk
from imednet.tlf.listings import SubjectListing

app = typer.Typer(
    help="Generate Tables, Listings, and Figures (TLFs).",
    no_args_is_help=True,
)
listing_app = typer.Typer(help="Generate listings.", no_args_is_help=True)
app.add_typer(listing_app, name="listing")


@listing_app.command("subject", help="Generate a subject listing.")
@with_sdk
def subject_listing(
    sdk: ImednetSDK,
    study_key: Annotated[str, typer.Argument(help="The key of the study.")],
    output_file: Annotated[
        str,
        typer.Option(
            "--output-file",
            "-o",
            help="Path to save the output CSV file.",
        ),
    ] = None,
):
    """
    Generate a subject listing for a given study.
    """
    report = SubjectListing(sdk=sdk, study_key=study_key, output_file=output_file)
    report.run()
