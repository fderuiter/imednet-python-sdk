"""TODO: Add docstring."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict

if TYPE_CHECKING:
    from airflow.exceptions import AirflowException

    try:
        # Airflow 3.x canonical Context import path.
        from airflow.sdk import Context
    except (ImportError, ModuleNotFoundError):
        # Airflow 2.x and compatibility fallback path.
        from airflow.utils.context import Context  # type: ignore[no-redef,attr-defined]

    try:
        from airflow.sdk.bases.hook import BaseHook
    except (ImportError, ModuleNotFoundError):
        from airflow.hooks.base import BaseHook  # type: ignore[no-redef,attr-defined]
else:  # pragma: no cover - typing fallback for optional Airflow dependency
    try:
        from airflow.sdk import Context  # type: ignore[no-redef]
    except (ImportError, ModuleNotFoundError):
        try:
            from airflow.utils.context import Context  # type: ignore[no-redef]
        except (ImportError, ModuleNotFoundError):
            Context = Dict[str, Any]
    try:
        from airflow.sdk.bases.hook import BaseHook
    except (ImportError, ModuleNotFoundError):
        from airflow.hooks.base import BaseHook

    try:
        from airflow.exceptions import AirflowException
    except (ImportError, ModuleNotFoundError):

        class _FallbackAirflowError(Exception):
            """TODO: Add docstring."""

            pass

        AirflowException = _FallbackAirflowError
