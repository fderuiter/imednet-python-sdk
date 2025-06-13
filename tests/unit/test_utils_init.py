import pytest
from imednet import utils


def test_lazy_load_pandas_functions() -> None:
    func = utils.records_to_dataframe
    from imednet.utils.pandas import records_to_dataframe as expected_rtodf

    assert func is expected_rtodf
    func2 = utils.export_records_csv
    from imednet.utils.pandas import export_records_csv as expected_export

    assert func2 is expected_export


def test_lazy_load_schema_objects() -> None:
    cache_cls = utils.SchemaCache
    from imednet.utils.schema import SchemaCache as ExpectedCache
    from imednet.utils.schema import SchemaValidator as ExpectedValidator
    from imednet.utils.schema import validate_record_data as expected_validate

    assert cache_cls is ExpectedCache
    assert utils.SchemaValidator is ExpectedValidator
    assert utils.validate_record_data is expected_validate


def test_getattr_unknown() -> None:
    with pytest.raises(AttributeError):
        getattr(utils, "does_not_exist")
