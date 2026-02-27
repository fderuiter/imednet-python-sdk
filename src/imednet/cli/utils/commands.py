from __future__ import annotations

from typing import List

import typer

from imednet.cli.decorators import with_sdk
from imednet.sdk import ImednetSDK

from .args import STUDY_KEY_ARG
from .context import fetching_status
from .output import display_list


def register_list_command(
    app: typer.Typer,
    attr: str,
    name: str,
    *,
    requires_study_key: bool = True,
    empty_msg: str | None = None,
    summary_fields: List[str] | None = None,
) -> None:
    """Attach a standard ``list`` command to ``app``."""

    if requires_study_key:

        @app.command("list")
        @with_sdk
        def list_cmd(sdk: ImednetSDK, study_key: str = STUDY_KEY_ARG) -> None:
            with fetching_status(name, study_key):
                items = getattr(sdk, attr).list(study_key)
            display_list(items, name, empty_msg, fields=summary_fields)

        return

    else:

        @app.command("list")
        @with_sdk
        def list_cmd_no_study(sdk: ImednetSDK) -> None:
            with fetching_status(name):
                items = getattr(sdk, attr).list()
            display_list(items, name, empty_msg, fields=summary_fields)

        return
