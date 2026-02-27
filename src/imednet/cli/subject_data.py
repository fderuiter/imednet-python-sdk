from __future__ import annotations

import typer
from rich import print

from ..sdk import ImednetSDK
from .decorators import with_sdk
from .utils import STUDY_KEY_ARG


@with_sdk
def subject_data(
    sdk: ImednetSDK,
    study_key: str = STUDY_KEY_ARG,
    subject_key: str = typer.Argument(..., help="The key identifying the subject."),
) -> None:
    """Retrieve all data for a single subject."""
    from . import SubjectDataWorkflow

    workflow = SubjectDataWorkflow(sdk)
    data = workflow.get_all_subject_data(study_key, subject_key)
    print(data.model_dump())
