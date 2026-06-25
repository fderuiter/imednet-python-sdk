"""Test Utils Typing module."""

import importlib
import sys
from typing import Any

import pandas as pd

from imednet.utils.typing import DataFrame


def test_dataframe_alias() -> None:
    """Test the test dataframe alias functionality."""
    assert DataFrame is pd.DataFrame


def test_dataframe_alias_without_pandas(monkeypatch):
    """Test the test dataframe alias without pandas functionality."""
    monkeypatch.setitem(sys.modules, "pandas", None)
    mod = importlib.reload(importlib.import_module("imednet.utils.typing"))
    assert mod.DataFrame is Any
