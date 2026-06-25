""" Airflow Compat module."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict

if TYPE_CHECKING:
    from airflow.exceptions import AirflowException
    from airflow.sdk.definitions.context import Context
else:  # pragma: no cover - typing fallback for optional Airflow dependency
    try:
        from airflow.sdk.definitions.context import Context  # type: ignore
    except (ImportError, ModuleNotFoundError):
        Context = Dict[str, Any]
    try:
        from airflow.exceptions import AirflowException
    except (ImportError, ModuleNotFoundError):

        class _FallbackAirflowError(Exception):
            """Implementation of the _FallbackAirflowError class."""

            pass

        AirflowException = _FallbackAirflowError
