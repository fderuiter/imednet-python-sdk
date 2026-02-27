"""Airflow operators for interacting with iMednet."""

from __future__ import annotations

import json
from typing import Any, Dict, Iterable, Optional

try:  # pragma: no cover - optional Airflow dependency
    from airflow.exceptions import AirflowException  # type: ignore
    from airflow.models import BaseOperator  # type: ignore
    from airflow.providers.amazon.aws.hooks.s3 import S3Hook as _S3Hook  # type: ignore
except Exception:  # pragma: no cover - placeholder fallback
    AirflowException = Exception

    class BaseOperator:  # type: ignore
        template_fields: Iterable[str] = ()

        def __init__(self, *args: Any, **kwargs: Any) -> None:  # pragma: no cover
            pass

    class _S3Hook:  # type: ignore
        def __init__(self, *args: Any, **kwargs: Any) -> None:  # pragma: no cover
            pass

        def load_string(self, *args: Any, **kwargs: Any) -> None:  # pragma: no cover
            pass


from ....sdk import ImednetSDK


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
        from . import ImednetHook

        return ImednetHook(self.imednet_conn_id).get_conn()

    def execute(self, context: Dict[str, Any]) -> str:
        sdk = self._get_sdk()
        endpoint_obj = getattr(sdk, self.endpoint)
        if hasattr(endpoint_obj, "list"):
            data = endpoint_obj.list(self.study_key, **self.endpoint_kwargs)
        else:
            raise AirflowException(f"Endpoint '{self.endpoint}' has no list method")
        records = [d.model_dump() if hasattr(d, "model_dump") else d for d in data]
        from . import S3Hook

        hook = S3Hook(aws_conn_id=self.aws_conn_id)
        hook.load_string(json.dumps(records), self.s3_key, self.s3_bucket, replace=True)
        return self.s3_key


S3Hook = _S3Hook

__all__ = ["ImednetToS3Operator", "S3Hook", "AirflowException"]
