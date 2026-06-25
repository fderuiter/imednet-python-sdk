"""Test Airflow Export module."""

import sys
from types import ModuleType
from unittest.mock import patch

import pytest


# Setup dummy airflow modules to prevent import errors if airflow is not installed
def _setup_airflow(monkeypatch):
    """Test the setup airflow functionality."""
    airflow_mod = ModuleType("airflow")
    hooks_pkg = ModuleType("airflow.hooks")
    hooks_mod = ModuleType("airflow.sdk.bases.hook")
    sdk_mod = ModuleType("airflow.sdk")
    sdk_bases = ModuleType("airflow.sdk.bases")
    sdk_defs = ModuleType("airflow.sdk.definitions")
    sdk_ctx = ModuleType("airflow.sdk.definitions.context")
    models_mod = ModuleType("airflow.models")

    class DummyBaseHook:
        """Test suite for DummyBaseHook."""

        @classmethod
        def get_connection(cls, conn_id):
            """Test the get connection functionality."""
            raise NotImplementedError

    class DummyBaseOperator:
        """Test suite for DummyBaseOperator."""

        template_fields = ()

        def __init__(self, **kwargs):
            """Initialize a new instance."""
            pass

    hooks_mod.BaseHook = DummyBaseHook
    models_mod.BaseOperator = DummyBaseOperator

    sdk_bases.hook = hooks_mod
    sdk_mod.bases = sdk_bases
    sdk_defs.context = sdk_ctx
    sdk_mod.definitions = sdk_defs
    airflow_mod.sdk = sdk_mod
    airflow_mod.hooks = hooks_pkg
    airflow_mod.models = models_mod

    monkeypatch.setitem(sys.modules, "airflow", airflow_mod)
    monkeypatch.setitem(sys.modules, "airflow.hooks", hooks_pkg)
    monkeypatch.setitem(sys.modules, "airflow.sdk.bases.hook", hooks_mod)
    monkeypatch.setitem(sys.modules, "airflow.sdk", sdk_mod)
    monkeypatch.setitem(sys.modules, "airflow.sdk.bases", sdk_bases)
    monkeypatch.setitem(sys.modules, "airflow.sdk.definitions", sdk_defs)
    monkeypatch.setitem(sys.modules, "airflow.sdk.definitions.context", sdk_ctx)
    monkeypatch.setitem(sys.modules, "airflow.models", models_mod)


EXPORT_FUNCTIONS = [
    "export_to_csv",
    "export_to_parquet",
    "export_to_excel",
    "export_to_json",
    "export_to_sql",
    "export_to_sql_by_form",
]


@pytest.fixture(autouse=True)
def setup_airflow_mock(monkeypatch):
    """Test the setup airflow mock functionality."""
    _setup_airflow(monkeypatch)


@pytest.mark.parametrize("func_name", EXPORT_FUNCTIONS)
def test_airflow_export_forwards_arguments(func_name: str) -> None:
    """Test that each airflow export function forwards arguments to the base export module."""
    # We import the export module inside the test to ensure the mock airflow modules are picked up.
    from apache_airflow_providers_imednet import export

    # Arrange
    airflow_func = getattr(export, func_name)
    base_export_path = f"imednet.integrations.export.{func_name}"

    args = ("arg1", 42)
    kwargs = {"key1": "value1", "key2": True}

    # Act & Assert
    with patch(base_export_path) as mock_base_func:
        airflow_func(*args, **kwargs)
        mock_base_func.assert_called_once_with(*args, **kwargs)
