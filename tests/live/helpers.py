"""Helpers for discovering study and form keys during live tests."""

import pytest

from imednet.sdk import ImednetSDK


def get_study_key(sdk: ImednetSDK) -> str:
    """Return the first study key available for the provided SDK.

    Raises a pytest skip exception if no studies are available.
    """
    studies = sdk.studies.list()
    if not studies:
        raise pytest.skip.Exception("No studies available for live tests")
    return studies[0].study_key


def get_form_key(sdk: ImednetSDK, study_key: str) -> str:
    """Return the first form key for ``study_key``.

    Raises a pytest skip exception if no forms are available.
    """
    forms = sdk.forms.list(study_key=study_key)
    if not forms:
        raise pytest.skip.Exception("No forms available for record creation")
    return forms[0].form_key
