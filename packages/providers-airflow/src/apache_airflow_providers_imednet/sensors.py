"""Airflow sensors for iMednet operations."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

try:  # pragma: no cover - optional Airflow dependency
    from airflow.sensors.base import BaseSensorOperator
except (ImportError, ModuleNotFoundError):  # pragma: no cover - placeholder fallback

    class BaseSensorOperator:  # type: ignore
        """Fallback BaseSensorOperator."""

        template_fields: Sequence[str] = ()

        def __init__(self, *args: Any, **kwargs: Any) -> None:  # pragma: no cover
            """Initialize fallback BaseSensorOperator."""
            pass


from imednet import ImednetSDK

from ._airflow_compat import AirflowException, Context
from .hooks import ImednetHook


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
        """Initialize the job sensor.

        :param study_key: The study key identifier.
        :param batch_id: The batch or job identifier to monitor.
        :param imednet_conn_id: Airflow connection ID to use for credentials.
        :param poke_interval: Seconds between polling attempts.
        :param kwargs: Additional Airflow BaseSensorOperator arguments.
        """
        super().__init__(poke_interval=poke_interval, **kwargs)
        self.study_key = study_key
        self.batch_id = batch_id
        self.imednet_conn_id = imednet_conn_id

    def _get_sdk(self) -> ImednetSDK:
        """Get the Imednet SDK client."""
        return ImednetHook(self.imednet_conn_id).get_sdk_client()

    def poke(self, context: Context) -> bool:
        """Check the status of the job."""
        from imednet.spi.models import JobStatus
        from imednet.spi.utils import JobFailedError, evaluate_job_state

        sdk = self._get_sdk()
        job: JobStatus = sdk.jobs.get(self.study_key, self.batch_id)

        try:
            return evaluate_job_state(job)
        except JobFailedError as e:
            raise AirflowException(str(e)) from e


__all__ = ["ImednetJobSensor"]
