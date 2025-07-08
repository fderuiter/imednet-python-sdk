from __future__ import annotations

from importlib import reload
import sys

from .. import export

if "imednet.integrations.airflow.hooks" in sys.modules:
    reload(sys.modules["imednet.integrations.airflow.hooks"])
if "imednet.integrations.airflow.operators" in sys.modules:
    reload(sys.modules["imednet.integrations.airflow.operators"])
if "imednet.integrations.airflow.sensors" in sys.modules:
    reload(sys.modules["imednet.integrations.airflow.sensors"])

from .hooks import ImednetHook
from .operators import ImednetExportOperator, ImednetToS3Operator

try:  # pragma: no cover - optional Airflow dependencies may be missing
    from .sensors import ImednetJobSensor
except Exception:  # pragma: no cover - sensor requires Airflow extras
    ImednetJobSensor = None  # type: ignore

__all__ = [
    "ImednetHook",
    "ImednetToS3Operator",
    "ImednetJobSensor",
    "ImednetExportOperator",
    "export",
]
