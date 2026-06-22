"""TODO: Add docstring."""

from imednet.utils import records_to_dataframe
from imednet.validation.cache import SchemaCache


def test_lazy_attrs_available() -> None:
    """TODO: Add docstring."""
    assert callable(records_to_dataframe)
    assert isinstance(SchemaCache, type)
