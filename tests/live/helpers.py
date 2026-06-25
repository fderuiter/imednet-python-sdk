"""Helpers for discovering study and form keys during live tests."""

import os
from typing import NoReturn

import pytest

from imednet.discovery import NoLiveDataError
from imednet.discovery import discover_form_key as _discover_form_key
from imednet.discovery import discover_study_key as _discover_study_key
from imednet.sdk import ImednetSDK

_STUDY_KEY_OVERRIDE = os.getenv("IMEDNET_STUDY_KEY")
_FORM_KEY_OVERRIDE = os.getenv("IMEDNET_FORM_KEY")


def _skip(msg: str) -> NoReturn:
    """Test the skip functionality."""
    pytest.skip(msg)
    raise AssertionError("unreachable")


def require_mutation() -> None:
    """Skip the calling test unless ``IMEDNET_ALLOW_MUTATION=1`` is set.

    Call this at the top of any test that creates or modifies data so that the
    mutation gate is enforced uniformly across the live suite.
    """
    if os.getenv("IMEDNET_ALLOW_MUTATION") != "1":
        pytest.skip("Set IMEDNET_ALLOW_MUTATION=1 to run mutation tests")


def get_study_key(sdk: ImednetSDK) -> str:
    """Return the study key to use for live tests.

    If ``IMEDNET_STUDY_KEY`` is set it is returned directly without querying
    the API.  Otherwise the first available study is discovered.
    """
    if _STUDY_KEY_OVERRIDE:
        return _STUDY_KEY_OVERRIDE
    try:
        return _discover_study_key(sdk)
    except NoLiveDataError as exc:
        _skip(str(exc))


def get_form_key(sdk: ImednetSDK, study_key: str) -> str:
    """Return the form key to use for record-creation tests.

    If ``IMEDNET_FORM_KEY`` is set it is returned directly.  Otherwise the
    first eligible form is discovered.
    """
    if _FORM_KEY_OVERRIDE:
        return _FORM_KEY_OVERRIDE
    try:
        return _discover_form_key(sdk, study_key)
    except NoLiveDataError as exc:
        _skip(str(exc))
