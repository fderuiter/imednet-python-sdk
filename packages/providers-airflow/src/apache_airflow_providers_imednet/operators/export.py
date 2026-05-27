"""Airflow operator for exporting study records."""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from typing import Any, cast

from imednet.sdk import ImednetSDK

from .. import export
from .._airflow_compat import AirflowException, Context
from ..hooks import ImednetHook

try:  # pragma: no cover - optional Airflow dependency
    from airflow.models import BaseOperator  # type: ignore
except (ImportError, ModuleNotFoundError):  # pragma: no cover - placeholder fallback

    class BaseOperator:  # type: ignore
        template_fields: Sequence[str] = ()

        def __init__(self, *args: Any, **kwargs: Any) -> None:
            pass


_ALLOWED_EXPORT_FUNCTIONS = frozenset(export.__all__)


class ImednetExportOperator(BaseOperator):
    """Export study records using helpers from :mod:`imednet.integrations.export`."""

    # Fields intended for Airflow `.partial().expand()` runtime mapping.
    mapped_runtime_fields: Sequence[str] = ("study_key", "output_path", "export_kwargs")
    template_fields: Sequence[str] = mapped_runtime_fields
    template_fields_renderers = {"export_kwargs": "json"}

    def __init__(
        self,
        *,
        study_key: str,
        output_path: str,
        export_func: str = "export_to_csv",
        export_kwargs: Mapping[str, Any] | None = None,
        imednet_conn_id: str = "imednet_default",
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.study_key = study_key
        self.output_path = output_path
        self.export_func = export_func
        self.export_kwargs = dict(export_kwargs or {})
        self.imednet_conn_id = imednet_conn_id

    def _get_export_callable(self) -> Callable[..., None]:
        """Return a supported export helper or raise for unknown helper names."""
        if self.export_func not in _ALLOWED_EXPORT_FUNCTIONS:
            supported = ", ".join(sorted(_ALLOWED_EXPORT_FUNCTIONS))
            raise AirflowException(
                f"Unsupported export_func '{self.export_func}'. Expected one of: {supported}"
            )
        return cast(Callable[..., None], getattr(export, self.export_func))

    def _get_sdk(self) -> ImednetSDK:
        """Resolve the SDK client from the configured Airflow connection at execute time."""
        return ImednetHook(self.imednet_conn_id).get_sdk_client()

    def _get_runtime_export_kwargs(self) -> dict[str, Any]:
        """Return a defensive copy of export kwargs for mapped task isolation."""
        return dict(self.export_kwargs)

    def execute(self, context: Context) -> str:
        export_callable = self._get_export_callable()
        sdk = self._get_sdk()
        export_callable(
            sdk,
            self.study_key,
            self.output_path,
            **self._get_runtime_export_kwargs(),
        )
        return self.output_path


__all__ = ["ImednetExportOperator"]
