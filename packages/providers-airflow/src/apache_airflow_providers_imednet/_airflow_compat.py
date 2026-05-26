from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict

if TYPE_CHECKING:
    import importlib

    from airflow.exceptions import AirflowException

    try:
        _airflow_context = importlib.import_module("airflow.sdk.definitions.context")
    except (ImportError, ModuleNotFoundError):
        _airflow_context = importlib.import_module("airflow.utils.context")

    Context = _airflow_context.Context
else:  # pragma: no cover - typing fallback for optional Airflow dependency
    Context = Dict[str, Any]
    try:
        from airflow.exceptions import AirflowException
    except (ImportError, ModuleNotFoundError):

        class _FallbackAirflowError(Exception):
            pass

        AirflowException = _FallbackAirflowError
