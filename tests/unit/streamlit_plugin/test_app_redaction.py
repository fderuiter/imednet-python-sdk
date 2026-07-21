"""Unit tests for app redaction."""

from __future__ import annotations

import streamlit as st


def test_sanitize_body_string():
    """Test that sanitize body string."""
    from imednet_streamlit.app import _sanitize_body

    res = _sanitize_body("mongodb://user:password123@host:27017")
    assert res == "mongodb://user:***@host:27017"


def test_sanitize_body_exception():
    """Test that sanitize body exception."""
    from imednet_streamlit.app import _sanitize_body

    ex = ValueError("mongodb://user:password123@host:27017")
    res = _sanitize_body(ex)
    assert isinstance(res, ValueError)
    assert str(res) == "mongodb://user:***@host:27017"


def test_sanitize_body_unprintable_exception():
    """Test that sanitize body unprintable exception."""
    from imednet_streamlit.app import _sanitize_body

    class BadError(Exception):
        """Test suite for BadError."""

        def __str__(self):
            """Helper function to   str  ."""
            raise RuntimeError("Cannot print")

        def __init__(self, msg=None):
            """Initialize the test object."""
            if msg == "<unprintable exception>":
                raise RuntimeError("Failed init")
            super().__init__(msg)

    ex = BadError()
    res = _sanitize_body(ex)
    # The instantiation of type(body) will fail, falling back to Exception
    assert type(res) is Exception
    assert "BadError: <unprintable exception>" in str(res)


def test_sanitize_body_non_string():
    """Test that sanitize body non string."""
    from imednet_streamlit.app import _sanitize_body

    res = _sanitize_body(123)
    assert res == 123


def test_secure_st_methods(monkeypatch):
    """Test that secure st methods."""
    from imednet_streamlit.app import (
        secure_st_error,
        secure_st_exception,
        secure_st_info,
        secure_st_warning,
    )

    calls = {}

    def mock_error(msg, *args, **kwargs):
        """Helper function to mock error."""
        calls["error"] = msg

    def mock_exception(msg, *args, **kwargs):
        """Helper function to mock exception."""
        calls["exception"] = msg

    def mock_warning(msg, *args, **kwargs):
        """Helper function to mock warning."""
        calls["warning"] = msg

    def mock_info(msg, *args, **kwargs):
        """Helper function to mock info."""
        calls["info"] = msg

    import imednet_streamlit.app as app

    monkeypatch.setattr(app, "original_st_error", mock_error)
    monkeypatch.setattr(app, "original_st_exception", mock_exception)
    monkeypatch.setattr(app, "original_st_warning", mock_warning)
    monkeypatch.setattr(app, "original_st_info", mock_info)

    secure_st_error("mongodb://user:password123@host:27017")  # pragma: allowlist secret
    assert calls["error"] == "mongodb://user:***@host:27017"

    ex = ValueError("mongodb://user:password123@host:27017")
    secure_st_exception(ex)
    assert str(calls["exception"]) == "mongodb://user:***@host:27017"

    secure_st_warning("mongodb://user:password123@host:27017")  # pragma: allowlist secret
    assert calls["warning"] == "mongodb://user:***@host:27017"

    secure_st_info("mongodb://user:password123@host:27017")  # pragma: allowlist secret
    assert calls["info"] == "mongodb://user:***@host:27017"


class _FakeChart:
    """Test suite for  FakeChart."""

    def __init__(self, title="Test Chart"):
        """Initialize the test object."""
        self.title = title
        self.data = "dummy_data"

    def properties(self, description=None):
        """Helper function to properties."""
        self.description = description
        return self


def test_toggle_high_contrast():
    """Test that toggle high contrast."""
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
