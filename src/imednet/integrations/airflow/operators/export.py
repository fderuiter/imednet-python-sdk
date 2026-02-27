"""Airflow operator for exporting study records."""

from __future__ import annotations

from importlib import import_module
from typing import Any, Dict, Iterable, Optional

from airflow.models import BaseOperator

from .. import export


class ImednetExportOperator(BaseOperator):
    """Export study records using helpers from :mod:`imednet.integrations.export`."""

    template_fields: Iterable[str] = ("study_key", "output_path")

    def __init__(
        self,
        *,
        study_key: str,
        output_path: str,
        export_func: str = "export_to_csv",
        export_kwargs: Optional[Dict[str, Any]] = None,
        imednet_conn_id: str = "imednet_default",
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.study_key = study_key
        self.output_path = output_path
        self.export_func = export_func
        self.export_kwargs = export_kwargs or {}
        self.imednet_conn_id = imednet_conn_id

    def execute(self, context: Dict[str, Any]) -> str:
        import sys

        airflow_mod = sys.modules.get("imednet.integrations.airflow")
        if airflow_mod is None:  # pragma: no cover - module should already be loaded
            airflow_mod = import_module("imednet.integrations.airflow")
        hook = airflow_mod.ImednetHook(self.imednet_conn_id)
        sdk = hook.get_conn()
        export_callable = getattr(export, self.export_func)
        export_callable(sdk, self.study_key, self.output_path, **self.export_kwargs)
        return self.output_path


__all__ = ["ImednetExportOperator"]
