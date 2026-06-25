"""Tests for test_utils_typing."""

import importlib
import sys
from typing import Any

import pandas as pd

from imednet.utils.typing import DataFrame


def test_dataframe_alias() -> None:
    """Test test_dataframe_alias behavior."""
    assert DataFrame is pd.DataFrame


def test_dataframe_alias_without_pandas(monkeypatch):
    """Test test_dataframe_alias_without_pandas behavior."""
    monkeypatch.setitem(sys.modules, "pandas", None)
    mod = importlib.reload(importlib.import_module("imednet.utils.typing"))
    assert mod.DataFrame is Any
