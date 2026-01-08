import pytest
from imednet.utils.validators import parse_bool, parse_int_or_default, parse_list_or_default

def test_parse_bool_ignores_custom_truthiness():
    """
    Verify that parse_bool returns False for unknown types, ignoring their truthiness.

    This is a defensive test to ensure we don't accidentally start relying on
    implicit boolean conversion for complex objects, which could lead to
    unexpected behavior if we pass a Model or Client object.
    """
    class TruthyObject:
        def __bool__(self):
            return True

    class FalsyObject:
        def __bool__(self):
            return False

    class ErrorObject:
        def __bool__(self):
            raise ValueError("Should not be called")

    # All should return False because they are not int/float/str/bool instances
    assert parse_bool(TruthyObject()) is False
    assert parse_bool(FalsyObject()) is False
    assert parse_bool(ErrorObject()) is False

def test_parse_int_or_default_float_handling():
    """
    Verify the distinction between float inputs and float-string inputs.

    Current behavior:
    - float(3.5) -> 3 (int() truncation)
    - str("3.5") -> 0 (int() raises ValueError -> default)

    This test locks in this behavior to prevent silent regression if we
    switch to a 'smarter' parser (like float(v) -> int) or a stricter one.
    """
    # Direct float input is cast to int
    assert parse_int_or_default(3.5) == 3
    assert parse_int_or_default(3.9) == 3

    # String float input fails int() cast, triggering default
    assert parse_int_or_default("3.5", default=0) == 0
    assert parse_int_or_default("3.5", default=99) == 99

def test_parse_list_or_default_wraps_iterables():
    """
    Verify that non-list iterables (tuples, sets, generators) are wrapped in a list,
    not converted to a list of their elements.

    This defends against the assumption that `list(iterable)` logic is used.
    If we passed a tuple `(1, 2)`, we get `[(1, 2)]`, not `[1, 2]`.
    """
    # Tuple wrapping
    assert parse_list_or_default((1, 2)) == [(1, 2)]

    # Set wrapping
    assert parse_list_or_default({1, 2}) == [{1, 2}]

    # Generator wrapping
    gen = (x for x in range(3))
    result = parse_list_or_default(gen)
    assert result == [gen]
    assert list(result[0]) == [0, 1, 2]  # Verify the generator is still intact inside

def test_parse_list_or_default_preserves_strings():
    """
    Verify that strings are treated as atomic values, not iterables of characters.
    """
    assert parse_list_or_default("abc") == ["abc"]
