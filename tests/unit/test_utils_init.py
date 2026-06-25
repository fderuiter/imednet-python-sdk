"""Tests for test_utils_init."""

import pytest

from imednet import utils


def test_lazy_load_pandas_functions() -> None:
    """Test test_lazy_load_pandas_functions behavior."""
    func = utils.records_to_dataframe
    from imednet.utils.pandas import records_to_dataframe as expected_rtodf

    assert func is expected_rtodf
    func2 = utils.export_records_csv
    from imednet.utils.pandas import export_records_csv as expected_export

    assert func2 is expected_export


def test_lazy_load_arrow_function() -> None:
    """Test test_lazy_load_arrow_function behavior."""
    func = utils.to_arrow_table
    from imednet.utils.arrow import to_arrow_table as expected_to_arrow_table

    assert func is expected_to_arrow_table


def test_schema_objects_not_in_utils() -> None:
    """Test test_schema_objects_not_in_utils behavior."""
    with pytest.raises(AttributeError):
        getattr(utils, "SchemaCache")
    with pytest.raises(AttributeError):
        getattr(utils, "SchemaValidator")
    with pytest.raises(AttributeError):
        getattr(utils, "validate_record_data")


def test_getattr_unknown() -> None:
    """Test test_getattr_unknown behavior."""
    with pytest.raises(AttributeError):
        getattr(utils, "does_not_exist")
