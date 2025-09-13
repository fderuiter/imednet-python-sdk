"""Helpers for discovering study and form keys during live tests."""

from typing import NoReturn

import pytest

from imednet.api.discovery import NoLiveDataError
from imednet.api.discovery import discover_form_key as _discover_form_key
from imednet.api.discovery import discover_study_key as _discover_study_key
from imednet.sdk import ImednetSDK


def _skip(msg: str) -> NoReturn:
    pytest.skip(msg)
    raise AssertionError("unreachable")


def get_study_key(sdk: ImednetSDK) -> str:
    try:
        return _discover_study_key(sdk)
    except NoLiveDataError as exc:
        _skip(str(exc))


def get_form_key(sdk: ImednetSDK, study_key: str) -> str:
    try:
        return _discover_form_key(sdk, study_key)
    except NoLiveDataError as exc:
        _skip(str(exc))
