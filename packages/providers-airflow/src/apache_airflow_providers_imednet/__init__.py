"""Airflow provider for iMednet.

This package provides hooks, operators, and sensors for integrating iMednet
EDC data workflows into Apache Airflow pipelines.
"""

from __future__ import annotations

from importlib import import_module

from . import export
from .hooks import ImednetHook
from .operators import ImednetExportOperator

try:  # pragma: no cover - optional Airflow dependencies may be missing
    sensors = import_module("apache_airflow_providers_imednet.sensors")
    ImednetJobSensor = sensors.ImednetJobSensor
except (ImportError, ModuleNotFoundError):  # pragma: no cover - sensor requires Airflow extras
    ImednetJobSensor = None  # type: ignore
    sensors = None  # type: ignore

__all__ = [
    "ImednetExportOperator",
    "ImednetHook",
    "ImednetJobSensor",
    "export",
]
