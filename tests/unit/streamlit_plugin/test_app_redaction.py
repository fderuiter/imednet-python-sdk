from __future__ import annotations

import pytest
import streamlit as st


def test_sanitize_body_string():
    from imednet_streamlit.app import _sanitize_body
    res = _sanitize_body("mongodb://user:password123@host:27017")
    assert res == "mongodb://user:***@host:27017"

def test_sanitize_body_exception():
    from imednet_streamlit.app import _sanitize_body
    ex = ValueError("mongodb://user:password123@host:27017")
    res = _sanitize_body(ex)
    assert isinstance(res, ValueError)
    assert str(res) == "mongodb://user:***@host:27017"

def test_sanitize_body_unprintable_exception():
    from imednet_streamlit.app import _sanitize_body
    class BadError(Exception):
        def __str__(self):
            raise RuntimeError("Cannot print")
        def __init__(self, msg=None):
            if msg == "<unprintable exception>":
                raise RuntimeError("Failed init")
            super().__init__(msg)
    
    ex = BadError()
    res = _sanitize_body(ex)
    # The instantiation of type(body) will fail, falling back to Exception
    assert type(res) is Exception
    assert "BadError: <unprintable exception>" in str(res)

def test_sanitize_body_non_string():
    from imednet_streamlit.app import _sanitize_body
    res = _sanitize_body(123)
    assert res == 123

def test_secure_st_methods(monkeypatch):
    from imednet_streamlit.app import (
        secure_st_error,
        secure_st_exception,
        secure_st_info,
        secure_st_warning,
    )

    calls = {}
    def mock_error(msg, *args, **kwargs):
        calls["error"] = msg
    def mock_exception(msg, *args, **kwargs):
        calls["exception"] = msg
    def mock_warning(msg, *args, **kwargs):
        calls["warning"] = msg
    def mock_info(msg, *args, **kwargs):
        calls["info"] = msg

    import imednet_streamlit.app as app
    monkeypatch.setattr(app, "original_st_error", mock_error)
    monkeypatch.setattr(app, "original_st_exception", mock_exception)
    monkeypatch.setattr(app, "original_st_warning", mock_warning)
    monkeypatch.setattr(app, "original_st_info", mock_info)

    secure_st_error("mongodb://user:password123@host:27017")
    assert calls["error"] == "mongodb://user:***@host:27017"

    ex = ValueError("mongodb://user:password123@host:27017")
    secure_st_exception(ex)
    assert str(calls["exception"]) == "mongodb://user:***@host:27017"

    secure_st_warning("mongodb://user:password123@host:27017")
    assert calls["warning"] == "mongodb://user:***@host:27017"

    secure_st_info("mongodb://user:password123@host:27017")
    assert calls["info"] == "mongodb://user:***@host:27017"

class _FakeChart:
    def __init__(self, title="Test Chart"):
        self.title = title
        self.data = "dummy_data"
    def properties(self, description=None):
        self.description = description
        return self

def test_accessible_altair_chart(monkeypatch):
    import imednet_streamlit.app as app
    from imednet_streamlit.app import accessible_altair_chart

    calls = []
    def mock_original_altair_chart(chart, use_container_width, theme, **kwargs):
        calls.append((chart, use_container_width, theme))

    monkeypatch.setattr(app, "original_altair_chart", mock_original_altair_chart)

    chart = _FakeChart()
    accessible_altair_chart(chart, use_container_width=True, theme="streamlit")

    assert len(calls) == 1
    assert calls[0][0].description == "Data visualization for Test Chart"
    assert calls[0][1] is True
    assert calls[0][2] == "streamlit"

def test_accessible_altair_chart_dict_title(monkeypatch):
    import imednet_streamlit.app as app
    from imednet_streamlit.app import accessible_altair_chart

    calls = []
    def mock_original_altair_chart(chart, use_container_width, theme, **kwargs):
        calls.append(chart)

    monkeypatch.setattr(app, "original_altair_chart", mock_original_altair_chart)

    chart = _FakeChart(title={"text": "Dict Title Chart"})
    accessible_altair_chart(chart)

    assert len(calls) == 1
    assert calls[0].description == "Data visualization for Dict Title Chart"


def test_accessible_altair_chart_non_str_title(monkeypatch):
    import imednet_streamlit.app as app
    from imednet_streamlit.app import accessible_altair_chart
    monkeypatch.setattr(app, "original_altair_chart", lambda *args, **kwargs: None)
    chart = _FakeChart(title=123)
    accessible_altair_chart(chart)

def test_accessible_altair_chart_with_dataframe(monkeypatch):
    import pandas as pd

    import imednet_streamlit.app as app
    from imednet_streamlit.app import accessible_altair_chart

    calls = []
    def mock_original_altair_chart(*args, **kwargs):
        pass
    monkeypatch.setattr(app, "original_altair_chart", mock_original_altair_chart)

    class FakeExpander:
        def __init__(self, label, expanded):
            calls.append(("expander", label, expanded))
        def __enter__(self):
            return self
        def __exit__(self, *args):
            pass

    def mock_dataframe(df, use_container_width):
        calls.append(("dataframe", df, use_container_width))

    monkeypatch.setattr(st, "expander", FakeExpander)
    monkeypatch.setattr(st, "dataframe", mock_dataframe)

    chart = _FakeChart()
    chart.data = pd.DataFrame({"col": [1, 2]})
    accessible_altair_chart(chart, use_container_width=True)

    assert ("expander", "Tabular Data View: Test Chart", False) in calls
    assert calls[-1][0] == "dataframe"


def test_toggle_high_contrast():
    import imednet_streamlit.app as app
    # Set up session state and query params
    st.session_state["high_contrast"] = False
    st.query_params["high_contrast"] = "false"
    
    app.toggle_high_contrast()
    assert st.session_state["high_contrast"] is True
    assert st.query_params["high_contrast"] == "true"
    
    app.toggle_high_contrast()
    assert st.session_state["high_contrast"] is False
    assert "high_contrast" not in st.query_params

