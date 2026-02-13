import pytest
from imednet.utils.validators import parse_bool

@pytest.mark.parametrize(
    "input_val, expected",
    [
        ("1.0", True),
        ("0.0", False),
        ("1.000", True),
        ("-1.0", True),
        ("0.1", True),
        ("1e1", True),
        ("0e1", False),
        ("inf", True),
        ("-inf", True),
        # Consistency with float('nan') which is truthy
        ("nan", True),
        ("NaN", True),
        ("123.456", True),
        ("0.000", False),
    ],
)
def test_parse_bool_float_strings(input_val, expected):
    """
    Test that parse_bool correctly handles strings representing float values,
    ensuring consistency with float() and bool() behavior in Python.
    """
    assert parse_bool(input_val) is expected
