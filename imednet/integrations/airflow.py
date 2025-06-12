"""Airflow hook and operator utilities."""

from __future__ import annotations

import os
from typing import Any, Iterable

from airflow.hooks.base import BaseHook
from airflow.models import BaseOperator

from ..sdk import ImednetSDK
from ..utils import export_records_csv


class ImednetHook(BaseHook):
    """Retrieve an :class:`~imednet.sdk.ImednetSDK` from an Airflow connection."""

    conn_name_attr = "imednet_conn_id"
    default_conn_name = "imednet_default"
    conn_type = "imednet"
    hook_name = "iMednet"

    def __init__(self, imednet_conn_id: str | None = None) -> None:
        super().__init__()
        self.imednet_conn_id = imednet_conn_id or self.default_conn_name

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
    """Export records to a CSV file using :func:`~imednet.utils.export_records_csv`."""

    template_fields: Iterable[str] = ("study_key", "file_path")

    def __init__(
        self,
        *,
        study_key: str,
        file_path: str,
        flatten: bool = True,
        imednet_conn_id: str = ImednetHook.default_conn_name,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.study_key = study_key
        self.file_path = file_path
        self.flatten = flatten
        self.imednet_conn_id = imednet_conn_id

    def execute(self, context: dict[str, Any]) -> str:  # type: ignore[override]
        hook = ImednetHook(self.imednet_conn_id)
        sdk = hook.get_conn()
        export_records_csv(sdk, self.study_key, self.file_path, flatten=self.flatten)
        return self.file_path


__all__ = ["ImednetHook", "ImednetExportOperator"]
