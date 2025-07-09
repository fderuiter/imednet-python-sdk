import panel as pn
from examples.panel_ui import _collect_functions, create_app

from imednet import ImednetSDK


def test_collect_functions() -> None:
    sdk = ImednetSDK(api_key="x", security_key="y", base_url="https://example.com")
    funcs = _collect_functions(sdk)
    assert isinstance(funcs, dict)
    assert "get_studies" in funcs
    assert "jobs.async_get" in funcs


def test_create_app(monkeypatch) -> None:
    monkeypatch.setenv("IMEDNET_API_KEY", "x")
    monkeypatch.setenv("IMEDNET_SECURITY_KEY", "y")
    monkeypatch.setenv("IMEDNET_BASE_URL", "https://example.com")
    app = create_app()
    assert isinstance(app, pn.Column)


def test_create_app_no_functions(monkeypatch) -> None:
    monkeypatch.setenv("IMEDNET_API_KEY", "x")
    monkeypatch.setenv("IMEDNET_SECURITY_KEY", "y")
    monkeypatch.setenv("IMEDNET_BASE_URL", "https://example.com")
    monkeypatch.setattr("examples.panel_ui._collect_functions", lambda _: {})
    app = create_app()
    assert isinstance(app, pn.pane.Markdown)
