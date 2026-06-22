"""Airflow sensors for iMednet operations."""

from __future__ import annotations

from typing import Any, Sequence

try:  # pragma: no cover - optional Airflow dependency
    from airflow.sensors.base import BaseSensorOperator
except (ImportError, ModuleNotFoundError):  # pragma: no cover - placeholder fallback

    class BaseSensorOperator:  # type: ignore
        """TODO: Add docstring."""

        template_fields: Sequence[str] = ()

        def __init__(self, *args: Any, **kwargs: Any) -> None:  # pragma: no cover
            """TODO: Add docstring."""
            pass


from imednet import ImednetSDK

from ._airflow_compat import AirflowException, Context
from .hooks import ImednetHook

TERMINAL_STATES = {"COMPLETED", "SUCCESS", "FAILED", "CANCELLED"}


class ImednetJobSensor(BaseSensorOperator):
    """Poll iMednet for job completion."""

    template_fields: Sequence[str] = ("study_key", "batch_id")

    def __init__(
        self,
        *,
        study_key: str,
        batch_id: str,
        imednet_conn_id: str = "imednet_default",
        poke_interval: float = 60,
        **kwargs: Any,
    ) -> None:
        """TODO: Add docstring."""
        super().__init__(poke_interval=poke_interval, **kwargs)
        self.study_key = study_key
        self.batch_id = batch_id
        self.imednet_conn_id = imednet_conn_id

    def _get_sdk(self) -> ImednetSDK:
        """TODO: Add docstring."""
        return ImednetHook(self.imednet_conn_id).get_conn()

    def poke(self, context: Context) -> bool:
        """TODO: Add docstring."""
        sdk = self._get_sdk()
        job = sdk.jobs.get(self.study_key, self.batch_id)
        if not job.state:
            return True
        state = job.state.upper()
        if state in TERMINAL_STATES:
            if state not in ("COMPLETED", "SUCCESS"):
                raise AirflowException(f"Job {self.batch_id} ended in state {state}")
            return True
        return False


__all__ = ["ImednetJobSensor"]
