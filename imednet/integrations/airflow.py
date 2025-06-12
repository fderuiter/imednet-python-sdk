"""Airflow integration helpers for exporting study data."""

from __future__ import annotations

import os
from typing import Any, Dict, Iterable, Optional

from airflow.hooks.base import BaseHook
from airflow.models import BaseOperator

from ..sdk import ImednetSDK
from . import export


class ImednetHook(BaseHook):
    """Retrieve an :class:`ImednetSDK` instance from an Airflow connection."""

    def __init__(self, imednet_conn_id: str = "imednet_default") -> None:
        super().__init__()
        self.imednet_conn_id = imednet_conn_id

    def get_conn(self) -> ImednetSDK:  # type: ignore[override]
        conn = self.get_connection(self.imednet_conn_id)
        extras = conn.extra_dejson
        api_key = extras.get("api_key") or conn.login or os.getenv("IMEDNET_API_KEY")
        security_key = (
            extras.get("security_key") or conn.password or os.getenv("IMEDNET_SECURITY_KEY")
        )
        base_url = extras.get("base_url") or os.getenv("IMEDNET_BASE_URL")
        return ImednetSDK(api_key=api_key, security_key=security_key, base_url=base_url)


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
        hook = ImednetHook(self.imednet_conn_id)
        sdk = hook.get_conn()
        export_callable = getattr(export, self.export_func)
        export_callable(sdk, self.study_key, self.output_path, **self.export_kwargs)
        return self.output_path


__all__ = ["ImednetHook", "ImednetExportOperator"]
