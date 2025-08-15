"""Airflow sensors for iMednet operations."""

from __future__ import annotations

from typing import Any, Dict, Iterable

try:  # pragma: no cover - optional Airflow dependency
    from airflow.exceptions import AirflowException
    from airflow.sensors.base import BaseSensorOperator
except Exception:  # pragma: no cover - placeholder fallback
    AirflowException = Exception

    class BaseSensorOperator:  # type: ignore
        template_fields: Iterable[str] = ()

        def __init__(self, *args: Any, **kwargs: Any) -> None:  # pragma: no cover
            pass


from ...sdk import ImednetSDK
from .hooks import ImednetHook

TERMINAL_STATES = {"COMPLETED", "FAILED", "CANCELLED"}


class ImednetJobSensor(BaseSensorOperator):
    """Poll iMednet for job completion."""

    template_fields: Iterable[str] = ("study_key", "batch_id")

    def __init__(
        self,
        *,
        study_key: str,
        batch_id: str,
        imednet_conn_id: str = "imednet_default",
        poke_interval: float = 60,
        **kwargs: Any,
    ) -> None:
        super().__init__(poke_interval=poke_interval, **kwargs)
        self.study_key = study_key
        self.batch_id = batch_id
        self.imednet_conn_id = imednet_conn_id

    def _get_sdk(self) -> ImednetSDK:
        return ImednetHook(self.imednet_conn_id).get_conn()

    def poke(self, context: Dict[str, Any]) -> bool:
        sdk = self._get_sdk()
        job = sdk.jobs.get(self.study_key, self.batch_id)
        state = job.state.upper()
        if state in TERMINAL_STATES:
            if state != "COMPLETED":
                from .operators import AirflowException

                raise AirflowException(f"Job {self.batch_id} ended in state {state}")
            return True
        return False


__all__ = ["ImednetJobSensor", "ImednetHook"]
