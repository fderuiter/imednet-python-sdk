import importlib
import sys


def test_jsondict_type():
    from imednet.utils.typing import JsonDict

    d: JsonDict = {"a": 1, "b": "x"}
    assert isinstance(d, dict)
    assert "a" in d and "b" in d


def test_dataframe_import_success():
    import imednet.utils.typing as typing_mod
    import pandas as pd

    assert typing_mod.DataFrame is pd.DataFrame


def test_dataframe_import_fallback(monkeypatch):
    # Remove pandas from sys.modules and simulate ImportError
    module_name = "imednet.utils.typing"
    sys.modules.pop(module_name, None)
    monkeypatch.setitem(sys.modules, "pandas", None)
    typing_mod = importlib.reload(importlib.import_module(module_name))
    from typing import Any

    assert typing_mod.DataFrame is Any
