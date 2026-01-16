"""Endpoint for managing records (eCRF instances) in a study."""

from typing import Any, Dict, List, Optional, Union

from imednet.endpoints._mixins import CreateEndpointMixin, ListGetEndpoint
from imednet.models.jobs import Job
from imednet.models.records import Record
from imednet.validation.cache import SchemaCache, validate_record_data


class RecordsEndpoint(CreateEndpointMixin, ListGetEndpoint[Record]):
    """
    API endpoint for interacting with records (eCRF instances) in an iMedNet study.

    Provides methods to list, retrieve, and create records.
    """

    PATH = "records"
    MODEL = Record
    _id_param = "recordId"
    _pop_study_filter = False

    def _prepare_create_args(
        self,
        study_key: str,
        email_notify: Union[bool, str, None],
    ) -> tuple[str, Dict[str, str]]:
        path = self._build_path(study_key, self.PATH)
        headers = {}
        if email_notify is not None:
            if isinstance(email_notify, str):
                # Security: Prevent header injection via newlines
                if "\n" in email_notify or "\r" in email_notify:
                    raise ValueError("email_notify must not contain newlines")
                headers["x-email-notify"] = email_notify
            else:
                headers["x-email-notify"] = str(email_notify).lower()
        return path, headers

    def _validate_records_if_schema_present(
        self, schema: Optional[SchemaCache], records_data: List[Dict[str, Any]]
    ) -> None:
        if schema is not None:
            for rec in records_data:
                fk = rec.get("formKey") or rec.get("form_key")
                if not fk:
                    fid = rec.get("formId") or rec.get("form_id") or 0
                    fk = schema.form_key_from_id(fid)
                if fk:
                    validate_record_data(schema, fk, rec.get("data", {}))

    def create(
        self,
        study_key: str,
        records_data: List[Dict[str, Any]],
        email_notify: Union[bool, str, None] = None,  # Accept bool, str (email), or None
        *,
        schema: Optional[SchemaCache] = None,
    ) -> Job:
        """
        Create new records in a study.

        Args:
            study_key: Study identifier
            records_data: List of record data objects to create
            email_notify: Whether to send email notifications (True/False), or an
                email address as a string.
            schema: Optional :class:`SchemaCache` instance used for local
                validation.

        Returns:
            Job object with information about the created job
        """
        self._validate_records_if_schema_present(schema, records_data)
        path, headers = self._prepare_create_args(study_key, email_notify)

        return self._create_resource(  # type: ignore[return-value]
            self._client,
            path,
            json=records_data,
            headers=headers,
            response_model=Job,
        )

    async def async_create(
        self,
        study_key: str,
        records_data: List[Dict[str, Any]],
        email_notify: Union[bool, str, None] = None,
        *,
        schema: Optional[SchemaCache] = None,
    ) -> Job:
        """Asynchronous version of :meth:`create`."""
        self._require_async_client()
        self._validate_records_if_schema_present(schema, records_data)
        path, headers = self._prepare_create_args(study_key, email_notify)

        return await self._create_resource(
            self._async_client,
            path,
            json=records_data,
            headers=headers,
            response_model=Job,
        )

    def _list_impl(
        self,
        client: Any,
        paginator_cls: type[Any],
        *,
        study_key: Optional[str] = None,
        record_data_filter: Optional[str] = None,
        **filters: Any,
    ) -> Any:
        extra = {"recordDataFilter": record_data_filter} if record_data_filter else None
        return super()._list_impl(
            client,
            paginator_cls,
            study_key=study_key,
            extra_params=extra,
            **filters,
        )
