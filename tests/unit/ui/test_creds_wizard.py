import json
import os
import tkinter as tk

import pytest
from imednet.ui.creds_wizard import MednetTab


class DummyClient:
    def __init__(self, status: int = 200) -> None:
        self.status = status

    def list_studies(self, headers):  # noqa: D401 - simple stub
        class Resp:
            def __init__(self, status: int) -> None:
                self.status_code = status

            def json(self):
                return {"data": [{"studyKey": "ABC"}]}

            text = "error"

        return Resp(self.status)


class DummyStore:
    def __init__(self) -> None:
        self.saved: tuple[str, str] | None = None

    def save_secret(self, key: str, value: str) -> None:  # noqa: D401 - simple stub
        self.saved = (key, value)


def test_success_flow() -> None:
    if not os.environ.get("DISPLAY"):
        pytest.skip("No display available")
    root = tk.Tk()
    root.withdraw()
    store = DummyStore()
    tab = MednetTab(root, DummyClient(), store)
    tab.api_entry.insert(0, "A")
    tab.sec_entry.insert(0, "B")
    tab._on_studies_ready({"x-api-key": "A", "x-imn-security-key": "B"}, ["ABC"])

    assert tab.study_combo["state"] == "readonly"
    tab._save()
    assert store.saved is not None
    assert store.saved[0] == "mednet:ABC"
    assert json.loads(store.saved[1]) == {"x-api-key": "A", "x-imn-security-key": "B"}
    root.destroy()


def test_error_flow() -> None:
    if not os.environ.get("DISPLAY"):
        pytest.skip("No display available")
    root = tk.Tk()
    root.withdraw()
    store = DummyStore()
    tab = MednetTab(root, DummyClient(status=401), store)
    tab._on_studies_error(Exception("nope"))
    assert store.saved is None
    assert tab.study_combo["state"] == "disabled"
    root.destroy()
