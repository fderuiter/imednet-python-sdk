"""Airflow hook for retrieving an :class:`ImednetSDK` instance."""

from __future__ import annotations

import os

from airflow.hooks.base import BaseHook

from ...sdk import ImednetSDK


class ImednetHook(BaseHook):
    """Retrieve an :class:`ImednetSDK` instance from an Airflow connection."""

    def __init__(self, imednet_conn_id: str = "imednet_default") -> None:
        super().__init__()
        self.imednet_conn_id = imednet_conn_id

    def get_conn(self) -> ImednetSDK:  # type: ignore[override]
        from airflow.hooks.base import BaseHook

        conn = BaseHook.get_connection(self.imednet_conn_id)
        extras = conn.extra_dejson
        api_key = extras.get("api_key") or conn.login or os.getenv("IMEDNET_API_KEY")
        security_key = (
            extras.get("security_key") or conn.password or os.getenv("IMEDNET_SECURITY_KEY")
        )
        base_url = extras.get("base_url") or os.getenv("IMEDNET_BASE_URL")
        return ImednetSDK(api_key=api_key, security_key=security_key, base_url=base_url)


__all__ = ["ImednetHook"]
