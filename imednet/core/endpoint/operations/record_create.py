"""
Operation for creating records.

Encapsulates validation, header construction, and execution logic for record creation.
"""

from __future__ import annotations

from typing import Any, Callable, Dict, Generic, List, Optional, TypeVar, Union, cast

from imednet.constants import HEADER_EMAIL_NOTIFY
from imednet.core.protocols import AsyncRequestorProtocol, RequestorProtocol
from imednet.utils.security import validate_header_value
from imednet.validation.cache import BaseSchemaCache, validate_record_entry

T = TypeVar("T")


class RecordCreateOperation(Generic[T]):
    """
    Operation for creating records.

    Handles validation against schema and security checks for headers
    before executing the creation request.
    """

    def __init__(
        self,
        path: str,
        records_data: List[Dict[str, Any]],
        email_notify: Union[bool, str, None] = None,
        schema: Optional[BaseSchemaCache[Any]] = None,
    ) -> None:
        """
        Initialize the record creation operation.

        Args:
            path: The full API path for the request.
            records_data: List of record data objects to create.
            email_notify: Email notification setting.
            schema: Optional schema cache for validation.

        Raises:
            ValidationError: If record data is invalid against the schema.
            ValueError: If email_notify contains invalid characters.
        """
        self.path = path
        self.records_data = records_data
        self.email_notify = email_notify
        self.schema = schema

        self._validate()
        self.headers = self._build_headers()

    def _validate(self) -> None:
        """Validate records against schema if provided."""
        if self.schema is not None:
            for rec in self.records_data:
                validate_record_entry(self.schema, rec)

    def _build_headers(self) -> Dict[str, str]:
        """
        Build headers for record creation request.

        Returns:
            Dictionary of headers.

        Raises:
            ValueError: If email_notify contains newlines.
        """
        headers: Dict[str, str] = {}
        if self.email_notify is not None:
            if isinstance(self.email_notify, str):
                validate_header_value(self.email_notify)
                headers[HEADER_EMAIL_NOTIFY] = self.email_notify
            else:
                headers[HEADER_EMAIL_NOTIFY] = str(self.email_notify).lower()
        return headers

    def execute_sync(
        self,
        client: RequestorProtocol,
        parse_func: Callable[[Any], T],
    ) -> T:
        """
        Execute synchronous creation request.

        Args:
            client: The synchronous HTTP client.
            parse_func: Function to parse the response.

        Returns:
            The parsed response object.
        """
        response = client.post(
            self.path,
            json=self.records_data,
            headers=self.headers,
        )
        return parse_func(response.json())

    async def execute_async(
        self,
        client: AsyncRequestorProtocol,
        parse_func: Callable[[Any], T],
    ) -> T:
        """
        Execute asynchronous creation request.

        Args:
            client: The asynchronous HTTP client.
            parse_func: Function to parse the response.

        Returns:
            The parsed response object.
        """
        response = await client.post(
            self.path,
            json=self.records_data,
            headers=self.headers,
        )
        return parse_func(response.json())
