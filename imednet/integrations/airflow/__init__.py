from __future__ import annotations

from importlib import import_module

from . import export
from .hooks import ImednetHook
from .operators import ImednetExportOperator, ImednetToS3Operator

try:  # pragma: no cover - optional Airflow dependencies may be missing
    sensors = import_module("imednet.integrations.airflow.sensors")
    ImednetJobSensor = sensors.ImednetJobSensor
except Exception:  # pragma: no cover - sensor requires Airflow extras
    ImednetJobSensor = None  # type: ignore
    sensors = None  # type: ignore

__all__ = [
    "ImednetHook",
    "ImednetToS3Operator",
    "ImednetJobSensor",
    "ImednetExportOperator",
    "export",
]
