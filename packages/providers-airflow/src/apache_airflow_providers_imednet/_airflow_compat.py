from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict

if TYPE_CHECKING:
    from airflow.exceptions import AirflowException
    from airflow.utils.context import Context
else:  # pragma: no cover - typing fallback for optional Airflow dependency
    Context = Dict[str, Any]
    try:
        from airflow.exceptions import AirflowException
    except (ImportError, ModuleNotFoundError):

        class _FallbackAirflowError(Exception):
            pass

        AirflowException = _FallbackAirflowError
