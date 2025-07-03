"""Airflow operators for interacting with iMednet."""

from __future__ import annotations

import json
from typing import Any, Dict, Iterable, Optional

from airflow.exceptions import AirflowException
from airflow.models import BaseOperator
from airflow.providers.amazon.aws.hooks.s3 import S3Hook
from airflow.sensors.base import BaseSensorOperator

from ...sdk import ImednetSDK
from .hook import ImednetHook


class ImednetToS3Operator(BaseOperator):
    """Fetch data from iMednet and store it in S3 as JSON."""

    template_fields: Iterable[str] = ("study_key", "s3_key")

    def __init__(
        self,
        *,
        study_key: str,
        s3_bucket: str,
        s3_key: str,
        endpoint: str = "records",
        endpoint_kwargs: Optional[Dict[str, Any]] = None,
        imednet_conn_id: str = "imednet_default",
        aws_conn_id: str = "aws_default",
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.study_key = study_key
        self.s3_bucket = s3_bucket
        self.s3_key = s3_key
        self.endpoint = endpoint
        self.endpoint_kwargs = endpoint_kwargs or {}
        self.imednet_conn_id = imednet_conn_id
        self.aws_conn_id = aws_conn_id

    def _get_sdk(self) -> ImednetSDK:
        return ImednetHook(self.imednet_conn_id).get_conn()

    def execute(self, context: Dict[str, Any]) -> str:
        sdk = self._get_sdk()
        endpoint_obj = getattr(sdk, self.endpoint)
        if hasattr(endpoint_obj, "list"):
            data = endpoint_obj.list(self.study_key, **self.endpoint_kwargs)
        else:
            raise AirflowException(f"Endpoint '{self.endpoint}' has no list method")
        records = [d.model_dump() if hasattr(d, "model_dump") else d for d in data]
        hook = S3Hook(aws_conn_id=self.aws_conn_id)
        hook.load_string(json.dumps(records), self.s3_key, self.s3_bucket, replace=True)
        return self.s3_key


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
                raise AirflowException(f"Job {self.batch_id} ended in state {state}")
            return True
        return False


__all__ = ["ImednetToS3Operator", "ImednetJobSensor"]
