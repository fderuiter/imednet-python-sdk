from __future__ import annotations

from typing import Any, Dict

Context = Dict[str, Any]

try:
    from airflow.exceptions import AirflowException
except (ImportError, ModuleNotFoundError):

    class AirflowException(Exception):  # type: ignore[no-redef]
        pass


try:
    from airflow.hooks.base import BaseHook as AirflowBaseHook  # type: ignore[attr-defined]
except (ImportError, ModuleNotFoundError):

    class AirflowBaseHook:  # type: ignore[no-redef]
        @staticmethod
        def get_connection(conn_id: str) -> Any:
            raise NotImplementedError(
                "Apache Airflow is not installed. "
                "Install apache-airflow-providers-imednet[airflow] to use this feature."
            )
