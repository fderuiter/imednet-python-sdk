import json
import tkinter as tk

import httpx
import pytest
from imednet.ui.creds_wizard import MednetTab


class DummyStore:
    def __init__(self) -> None:
        self.saved: tuple[str, str] | None = None

    def save_secret(self, name: str, value: str) -> None:
        self.saved = (name, value)


class DummyClient:
    def __init__(self, response: httpx.Response) -> None:
        self.response = response
        self.called_with: dict[str, str] | None = None

    def list_studies(self, headers: dict[str, str]) -> httpx.Response:
        self.called_with = headers
        return self.response


def test_successful_verification(monkeypatch: pytest.MonkeyPatch) -> None:
    resp = httpx.Response(200, json={"data": [{"studyKey": "A"}, {"studyKey": "B"}]})
    client = DummyClient(resp)
    store = DummyStore()
    try:
        root = tk.Tk()
        root.withdraw()
    except tk.TclError:
        pytest.skip("Tk not available")
    tab = MednetTab(root, client, store)
    tab.api_entry.insert(0, "api")
    tab.sec_entry.insert(0, "sec")
    events: list[dict[str, object]] = []
    root.bind("<<MednetCredsVerified>>", lambda e: events.append(json.loads(e.data)))  # type: ignore[attr-defined]
    tab._on_success(["A", "B"], {"x-api-key": "api", "x-imn-security-key": "sec"})
    root.update()
    tab.save()
    assert tab.study_cb["state"] == "readonly"
    assert tab.study_cb["values"] == ("A", "B")
    assert store.saved is not None
    assert store.saved[0] == "mednet:A"
    assert json.loads(store.saved[1]) == {"x-api-key": "api", "x-imn-security-key": "sec"}
    assert events and events[0]["studyKey"] == "A"


def test_error_does_not_save(monkeypatch: pytest.MonkeyPatch) -> None:
    store = DummyStore()
    try:
        root = tk.Tk()
        root.withdraw()
    except tk.TclError:
        pytest.skip("Tk not available")
    tab = MednetTab(root, DummyClient(httpx.Response(401)), store)
    called: dict[str, bool] = {}
    monkeypatch.setattr(
        "ttkbootstrap.dialogs.Messagebox.show_error",
        lambda *_args, **_kw: called.setdefault("msg", True),
    )
    tab._on_error("bad")
    root.update()
    tab.save()
    assert called.get("msg") is True
    assert store.saved is None
    assert tab.study_cb["state"] == "disabled"
