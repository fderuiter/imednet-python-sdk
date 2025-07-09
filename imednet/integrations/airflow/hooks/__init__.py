"""Airflow hook for retrieving an :class:`ImednetSDK` instance."""

from airflow.hooks.base import BaseHook

from ....config import load_config
from ....sdk import ImednetSDK


class ImednetHook(BaseHook):
    """Retrieve an :class:`ImednetSDK` instance from an Airflow connection."""

    def __init__(self, imednet_conn_id: str = "imednet_default") -> None:
        super().__init__()
        self.imednet_conn_id = imednet_conn_id

    def get_conn(self) -> ImednetSDK:  # type: ignore[override]
        from airflow.hooks.base import BaseHook as CurrentBaseHook

        global BaseHook
        if BaseHook is not CurrentBaseHook:
            BaseHook = CurrentBaseHook

        conn = BaseHook.get_connection(self.imednet_conn_id)
        extras = conn.extra_dejson
        config = load_config(
            api_key=extras.get("api_key") or conn.login,
            security_key=extras.get("security_key") or conn.password,
            base_url=extras.get("base_url"),
        )
        return ImednetSDK(
            api_key=config.api_key,
            security_key=config.security_key,
            base_url=config.base_url,
        )


__all__ = ["ImednetHook"]
