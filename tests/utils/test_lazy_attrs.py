"""Tests for test_lazy_attrs."""

from imednet.utils import records_to_dataframe
from imednet.validation.cache import SchemaCache


def test_lazy_attrs_available() -> None:
    """Test test_lazy_attrs_available behavior."""
    assert callable(records_to_dataframe)
    assert isinstance(SchemaCache, type)
