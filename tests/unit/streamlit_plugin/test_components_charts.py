"""Test Components Charts module."""

from __future__ import annotations

import altair as alt
import pandas as pd

from imednet_streamlit.components import bar_chart, line_chart, pie_chart


def test_bar_chart_returns_altair_chart_with_defaults() -> None:
    """Test the test bar chart returns altair chart with defaults functionality."""
    df = pd.DataFrame({"category": ["A", "B"], "value": [1, 2]})
    chart = bar_chart(df, x="value", y="category", title="Example")

    assert isinstance(chart, alt.Chart)
    encoding = chart.encoding
    assert getattr(encoding, "color", None) is not None
    assert encoding.color.to_dict() == {"value": "#1f77b4"}


def test_bar_chart_returns_altair_chart_with_color_encoding() -> None:
    """Test the test bar chart returns altair chart with color encoding functionality."""
    df = pd.DataFrame({"category": ["A", "B"], "value": [1, 2], "group": ["X", "Y"]})
    chart = bar_chart(df, x="value", y="category", color="group", title="Example")

    assert isinstance(chart, alt.Chart)
    encoding = chart.encoding
    assert getattr(encoding, "color", None) is not None
    color_dict = encoding.color.to_dict()
    assert color_dict["field"] == "group"
    assert color_dict["type"] == "nominal"
    assert "scale" in color_dict


def test_line_chart_returns_altair_chart_with_defaults() -> None:
    """Test the test line chart returns altair chart with defaults functionality."""
    df = pd.DataFrame(
        {
            "date": pd.to_datetime(["2026-01-01", "2026-01-02"]),
            "count": [1, 2],
        }
    )
    chart = line_chart(df, x="date", y="count")

    assert isinstance(chart, alt.Chart)
    encoding = chart.encoding
    assert getattr(encoding, "color", None) is not None
    assert encoding.color.to_dict() == {"value": "#1f77b4"}


def test_line_chart_returns_altair_chart_with_color_encoding() -> None:
    """Test the test line chart returns altair chart with color encoding functionality."""
    df = pd.DataFrame(
        {
            "date": pd.to_datetime(["2026-01-01", "2026-01-02"]),
            "count": [1, 2],
            "group": ["X", "Y"],
        }
    )
    chart = line_chart(df, x="date", y="count", color="group")

    assert isinstance(chart, alt.Chart)
    encoding = chart.encoding
    assert getattr(encoding, "color", None) is not None
    color_dict = encoding.color.to_dict()
    assert color_dict["field"] == "group"
    assert color_dict["type"] == "nominal"


def test_pie_chart_returns_altair_chart() -> None:
    """Test the test pie chart returns altair chart functionality."""
    df = pd.DataFrame({"status": ["Open", "Closed"], "count": [4, 6]})
    chart = pie_chart(df, theta="count", color="status")

    assert isinstance(chart, alt.Chart)
    encoding = chart.encoding
    assert getattr(encoding, "color", None) is not None
    color_dict = encoding.color.to_dict()
    assert color_dict["field"] == "status"
    assert color_dict["type"] == "nominal"

    assert getattr(encoding, "theta", None) is not None
    theta_dict = encoding.theta.to_dict()
    assert theta_dict["field"] == "count"
    assert theta_dict["type"] == "quantitative"
