import pytest

from imednet.utils.security import sanitize_csv_formula


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
