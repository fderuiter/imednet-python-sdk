import pytest

from imednet.utils.validators import parse_dict_or_default


def test_parse_dict_or_default_with_dict():
    """Test that parse_dict_or_default returns the dict if it's a dict."""
    assert parse_dict_or_default({"a": 1}) == {"a": 1}


def test_parse_dict_or_default_with_none():
    """Test that parse_dict_or_default returns a default dict if it's None."""
    assert parse_dict_or_default(None) == {}


def test_parse_dict_or_default_with_none_and_factory():
    """Test that parse_dict_or_default respects the default_factory."""
    assert parse_dict_or_default(None, default_factory=lambda: {"a": 1}) == {"a": 1}


def test_parse_dict_or_default_with_invalid_type_fails():
    """Test that parse_dict_or_default raises TypeError for invalid types."""
    with pytest.raises(TypeError):
        parse_dict_or_default("not a dict")
    with pytest.raises(TypeError):
        parse_dict_or_default(123)
    with pytest.raises(TypeError):
        parse_dict_or_default([1, 2, 3])
