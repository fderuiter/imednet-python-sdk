import importlib

import pytest


def test_schema_module_exports_and_deprecation_warning() -> None:
    # First ensure we import it, and catch the warning so it doesn't fail strict CI
    with pytest.warns(
        DeprecationWarning,
        match="imednet.validation.schema is deprecated; use imednet.validation.cache",
    ):
        import imednet.validation.schema as schema

        # Reload it if it was already in sys.modules, so coverage picks it up during the test run
        importlib.reload(schema)

    assert hasattr(schema, "BaseSchemaCache")
    assert hasattr(schema, "SchemaValidator")
    assert hasattr(schema, "AsyncSchemaValidator")
    assert hasattr(schema, "validate_record_data")
