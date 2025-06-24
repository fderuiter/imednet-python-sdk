from imednet.utils import records_to_dataframe
from imednet.validation.schema import SchemaCache


def test_lazy_attrs_available() -> None:
    assert callable(records_to_dataframe)
    assert isinstance(SchemaCache, type)
