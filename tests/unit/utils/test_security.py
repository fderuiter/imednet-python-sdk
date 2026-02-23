import pytest

from imednet.utils.security import sanitize_csv_formula, validate_header_value


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
    assert sanitize_csv_formula(input_val) == expected


@pytest.mark.parametrize(
    "input_val",
    [
        "safe_value",
        "value with spaces",
        "value-with-dashes",
        "123",
        "",
    ],
)
def test_validate_header_value_success(input_val):
    assert validate_header_value(input_val) == input_val


@pytest.mark.parametrize(
    "input_val",
    [
        "header\nvalue",
        "header\rvalue",
        "header\r\nvalue",
        "\nheader",
        "header\n",
    ],
)
def test_validate_header_value_error(input_val):
    with pytest.raises(ValueError, match="Header value must not contain newlines"):
        validate_header_value(input_val)
