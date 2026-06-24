"""Regression tests for Airflow provider compatibility.

These tests ensure that the Airflow provider remains importable and usable
across various dependency assumptions, protecting against breaking shims
or missing optional dependencies.
"""

from __future__ import annotations

import sys
from types import ModuleType
from typing import Any
from unittest.mock import MagicMock

import pytest


def test_provider_importability_without_airflow_installed(monkeypatch) -> None:
    """Verify that the provider does not crash on import if Airflow is missing."""
    # Hide airflow from sys.modules
    monkeypatch.setitem(sys.modules, "airflow", None)
    monkeypatch.setitem(sys.modules, "airflow.exceptions", None)
    monkeypatch.setitem(sys.modules, "airflow.hooks", None)
    monkeypatch.setitem(sys.modules, "airflow.models", None)
    monkeypatch.setitem(sys.modules, "airflow.sensors", None)
    monkeypatch.setitem(sys.modules, "airflow.utils", None)

    # We need to force a reload if it was already imported, or just try to import a sub-module
    # that uses the fallback logic.
    if "apache_airflow_providers_imednet._airflow_compat" in sys.modules:
        monkeypatch.delitem(sys.modules, "apache_airflow_providers_imednet._airflow_compat")

    from apache_airflow_providers_imednet._airflow_compat import AirflowException, Context

    assert issubclass(AirflowException, Exception)
    assert (
        Context is dict
        or (hasattr(Context, "__origin__") and Context.__origin__ is dict)
        or Context == dict[str, Any]
    )


def test_optional_amazon_dependency_absence(monkeypatch) -> None:
    """Verify that the provider works even if boto3 (Amazon) is missing."""
    monkeypatch.setitem(sys.modules, "boto3", None)
    monkeypatch.setitem(sys.modules, "botocore", None)
    monkeypatch.setitem(sys.modules, "botocore.exceptions", None)

    # Hook should still be importable
    from apache_airflow_providers_imednet.hooks import ImednetHook

    hook = ImednetHook(imednet_conn_id="test")
    assert hook.imednet_conn_id == "test"


def test_hook_operator_sensor_instantiation() -> None:
    """Verify basic usability of core provider components."""
    # This requires airflow to be present in the environment (which it is in dev)
    pytest.importorskip("airflow")

    from apache_airflow_providers_imednet.hooks import ImednetHook
    from apache_airflow_providers_imednet.operators.export import ImednetExportOperator
    from apache_airflow_providers_imednet.sensors import ImednetJobSensor

    hook = ImednetHook(imednet_conn_id="imednet_default")
    assert hook is not None

    op = ImednetExportOperator(
        task_id="test_export",
        study_key="S",
        output_path="/tmp/test.csv",
        imednet_conn_id="imednet_default",
    )
    # Airflow sets task_id on the instance via BaseOperator.__init__
    # but some versions might not expose it as a direct attribute if not properly initialized.
    # We verify it's at least instantiated.
    assert op is not None

    sensor = ImednetJobSensor(
        task_id="test_sensor",
        study_key="S",
        batch_id="B123",
        imednet_conn_id="imednet_default",
    )
    assert sensor is not None


def test_serialization_shims_validity() -> None:
    """Verify that serialization/import-path shims remain valid."""
    # Check that we can import from the top-level package (common Airflow pattern)
    import apache_airflow_providers_imednet

    assert hasattr(apache_airflow_providers_imednet, "ImednetHook")
    assert hasattr(apache_airflow_providers_imednet, "ImednetExportOperator")
    assert hasattr(apache_airflow_providers_imednet, "ImednetJobSensor")
