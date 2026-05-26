"""Airflow operator for exporting study records."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, Optional, Sequence

if TYPE_CHECKING:
    from airflow.utils.context import Context
else:  # pragma: no cover - typing fallback for optional Airflow dependency
    Context = Dict[str, Any]

from airflow.models import BaseOperator

from .. import export
from ..hooks import ImednetHook


class ImednetExportOperator(BaseOperator):
    """Export study records using helpers from :mod:`imednet.integrations.export`."""

    template_fields: Sequence[str] = ("study_key", "output_path", "export_kwargs")

    def __init__(
        self,
        *,
        study_key: str,
        output_path: str,
        export_func: str = "export_to_csv",
        export_kwargs: Optional[Dict[str, Any]] = None,
        imednet_conn_id: str = "imednet_default",
        isolate_output_path: bool = False,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.study_key = study_key
        self.output_path = output_path
        self.export_func = export_func
        self.export_kwargs = export_kwargs or {}
        self.imednet_conn_id = imednet_conn_id
        self.isolate_output_path = isolate_output_path

    def execute(self, context: Context) -> str:
        hook = ImednetHook(self.imednet_conn_id)
        sdk = hook.get_sdk_client()
        export_callable = getattr(export, self.export_func)
        output_path = self._resolved_output_path(context)
        export_callable(sdk, self.study_key, output_path, **deepcopy(self.export_kwargs))
        return output_path

    def _resolved_output_path(self, context: Context) -> str:
        if not self.isolate_output_path:
            return self.output_path
        map_index = context.get("map_index")
        if map_index is None:
            task_instance = context.get("ti") or context.get("task_instance")
            map_index = getattr(task_instance, "map_index", None)
        suffix = "single" if map_index is None else str(map_index)
        path = Path(self.output_path)
        joined_suffix = "".join(path.suffixes)
        base_name = path.name[: -len(joined_suffix)] if joined_suffix else path.name
        return str(path.with_name(f"{base_name}__{suffix}{joined_suffix}"))


__all__ = ["ImednetExportOperator"]
