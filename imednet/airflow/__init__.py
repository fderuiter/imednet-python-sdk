"""Deprecated Airflow integration location."""

import warnings

from imednet.integrations.airflow import (
    ImednetExportOperator,
    ImednetHook,
    ImednetJobSensor,
    ImednetToS3Operator,
)

warnings.warn(
    "`imednet.airflow` is deprecated; use `imednet.integrations.airflow` instead",
    DeprecationWarning,
    stacklevel=2,
)

__all__ = [
    "ImednetHook",
    "ImednetToS3Operator",
    "ImednetJobSensor",
    "ImednetExportOperator",
]
