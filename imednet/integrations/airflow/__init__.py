from __future__ import annotations

import sys
from importlib import reload

from .. import export

if "imednet.integrations.airflow.hook" in sys.modules:
    reload(sys.modules["imednet.integrations.airflow.hook"])
if "imednet.integrations.airflow.export_operator" in sys.modules:
    reload(sys.modules["imednet.integrations.airflow.export_operator"])
if "imednet.integrations.airflow.operators" in sys.modules:
    reload(sys.modules["imednet.integrations.airflow.operators"])

from .export_operator import ImednetExportOperator
from .hook import ImednetHook

try:  # pragma: no cover - optional Airflow dependencies may be missing
    from .operators import ImednetJobSensor, ImednetToS3Operator
except Exception:  # pragma: no cover - operators require Airflow extras
    ImednetJobSensor = ImednetToS3Operator = None  # type: ignore

__all__ = [
    "ImednetHook",
    "ImednetToS3Operator",
    "ImednetJobSensor",
    "ImednetExportOperator",
    "export",
]
