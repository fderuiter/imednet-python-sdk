import pytest

from imednet import utils


def test_lazy_load_pandas_functions() -> None:
    func = utils.records_to_dataframe
    from imednet.utils.pandas import records_to_dataframe as expected_rtodf

    assert func is expected_rtodf
    func2 = utils.export_records_csv
    from imednet.utils.pandas import export_records_csv as expected_export

    assert func2 is expected_export


def test_schema_objects_not_in_utils() -> None:
    with pytest.raises(AttributeError):
        getattr(utils, "SchemaCache")
    with pytest.raises(AttributeError):
        getattr(utils, "SchemaValidator")
    with pytest.raises(AttributeError):
        getattr(utils, "validate_record_data")


def test_getattr_unknown() -> None:
    with pytest.raises(AttributeError):
        getattr(utils, "does_not_exist")
