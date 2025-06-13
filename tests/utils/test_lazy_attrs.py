from imednet.utils import SchemaCache, records_to_dataframe


def test_lazy_attrs_available() -> None:
    assert callable(records_to_dataframe)
    assert isinstance(SchemaCache, type)
