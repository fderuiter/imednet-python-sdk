"""Tests for test_security."""

import pytest

from imednet.errors import ClientError, PathTraversalValidationError
from imednet.utils.security import (
    sanitize_csv_formula,
    validate_header_value,
    validate_partition_key,
)


@pytest.mark.parametrize(
    "input_val, expected",
    [
        # Unsafe inputs (direct)
        ("=SUM(A1:A2)", "'=SUM(A1:A2)"),
        ("+1", "'+1"),
        ("-1", "'-1"),
        ("@foo", "'@foo"),
        # Unsafe inputs (whitespace bypass)
        ("   =cmd", "'   =cmd"),
        ("\t+1", "'\t+1"),
        ("\n-1", "'\n-1"),
        # Safe inputs
        ("hello", "hello"),
        ("123", "123"),
        ("", ""),
        (None, None),
        (1, 1),
        (1.5, 1.5),
        (True, True),
        # Mixed (safe)
        ("foo=bar", "foo=bar"),
        (" foo=bar", " foo=bar"),
    ],
)
def test_sanitize_csv_formula(input_val, expected):
    """Test test_sanitize_csv_formula behavior."""
    assert sanitize_csv_formula(input_val) == expected


@pytest.mark.parametrize(
    "input_val",
    [
        "application/json",
        "Bearer my-token-123",
        "Mozilla/5.0",
        "en-US,en;q=0.5",
        "",
        "custom_header_value",
    ],
)
def test_validate_header_value_valid(input_val):
    """Test test_validate_header_value_valid behavior."""
    validate_header_value(input_val)


@pytest.mark.parametrize(
    "input_val",
    [
        "invalid\nvalue",
        "invalid\rvalue",
        "invalid\r\nvalue",
        "\n",
        "\r",
        "Bearer \nmy-token",
        "Bearer my-token\n",
    ],
)
def test_validate_header_value_invalid(input_val):
    """Test test_validate_header_value_invalid behavior."""
    with pytest.raises(ClientError, match="Header value must not contain newlines"):
        validate_header_value(input_val)


@pytest.mark.parametrize(
    "input_val, expected",
    [
        (["=cmd", "safe"], ["'=cmd", "safe"]),
        (("unsafe", "+1"), ("unsafe", "'+1")),
        ([["-nested"], "@also_nested"], [["'-nested"], "'@also_nested"]),
    ],
)
def test_sanitize_csv_formula_collections(input_val, expected):
    """Test test_sanitize_csv_formula_collections behavior."""
    assert sanitize_csv_formula(input_val) == expected


@pytest.mark.parametrize("key", ["STUDY_A", "study-001", "visit 1"])
def test_validate_partition_key_valid(key: str) -> None:
    """Test test_validate_partition_key_valid behavior."""
    validate_partition_key(key)


@pytest.mark.parametrize(
    "key",
    [
        "../study",
        "..\\study",
        "/rooted",
        "\\rooted",
        "C:\\Windows",
        "C:/Windows",
        "study/form",
        "study\\form",
        "study\x00key",
        "..",
    ],
)
def test_validate_partition_key_invalid(key: str) -> None:
    """Test test_validate_partition_key_invalid behavior."""
    with pytest.raises(PathTraversalValidationError):
        validate_partition_key(key)
