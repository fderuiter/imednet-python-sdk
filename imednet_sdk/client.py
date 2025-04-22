"""
Core HTTP client for interacting with the iMednet API.

This module defines the `ImednetClient`, the primary entry point for using the SDK.
It handles:

- Authentication using API and Security keys (read from arguments or environment variables).
- Configuration of base URL, timeouts, and retry logic.
- Making HTTP requests (GET, POST) to the iMednet API.
- Automatic retry of failed requests based on configurable conditions (status codes,
  exceptions, methods) using the `tenacity` library.
- Parsing successful JSON responses into Pydantic models.
- Raising specific `ImednetSdkException` subclasses for API errors (4xx/5xx responses).
- Providing access to resource-specific clients (e.g., `studies`, `records`) via properties.

Typical usage involves initializing the client and then accessing resource clients:

.. code-block:: python

    from imednet_sdk import ImednetClient
    from imednet_sdk.exceptions import ImednetSdkException

    # Client uses environment variables IMEDNET_API_KEY, IMEDNET_SECURITY_KEY, IMEDNET_BASE_URL by default
    client = ImednetClient()

    try:
        response = client.studies.list_studies(size=10)
        if response and response.data:
            for study in response.data:
                print(f"Study: {study.studyName} (Key: {study.studyKey})")
    except ImednetSdkException as e:
        print(f"API Error: {e}")

This module is part of the iMednet SDK, designed for seamless interaction with the iMednet
API, enabling efficient data management and retrieval for clinical studies.
"""

import datetime  # Added for timestamp
import logging
import os
# Add necessary imports for type hints
from typing import Any, Dict, List, Optional, Set, Type, TypeVar, Union

import httpx
from pydantic import BaseModel, TypeAdapter, ValidationError
# Import tenacity for retry logic
from tenacity import RetryError, Retrying, stop_after_attempt, wait_exponential

from imednet_sdk.models._common import ApiResponse

# Import resource clients
from .api import (CodingsClient, FormsClient, IntervalsClient, JobsClient, RecordRevisionsClient,
                  RecordsClient, SitesClient, StudiesClient, SubjectsClient, UsersClient,
                  VariablesClient, VisitsClient)
# Import custom exceptions
from .exceptions import (ApiError, AuthenticationError, AuthorizationError, BadRequestError,
                         ImednetSdkException, NotFoundError, RateLimitError)
from .exceptions import ValidationError as SdkValidationError  # Alias to avoid name clash
# Import the new helper function
from .utils import _fetch_and_parse_typed_records

logger = logging.getLogger(__name__)

# Define a TypeVar for generic response models
T = TypeVar("T", bound=BaseModel)

# Type alias for timeout configuration
TimeoutTypes = Union[float, httpx.Timeout, None]

# Define retryable exceptions and status codes - Updated for tenacity
# Default exceptions to retry on (network errors + specific API errors)
DEFAULT_RETRY_EXCEPTIONS: Set[type] = {
    httpx.ConnectError,
    httpx.ReadTimeout,
    httpx.PoolTimeout,
    httpx.ConnectTimeout,
    RateLimitError,  # Retry on 429
    ApiError,  # Retry on 5xx by default (ApiError is raised for 5xx)
}
# Default methods considered idempotent and safe to retry
DEFAULT_RETRY_METHODS: Set[str] = {"GET"}  # Only retry GET by default


class ImednetClient:
    """Core HTTP client for authenticated interaction with the iMednet API.

    Manages HTTP connections, authentication headers, request execution with retries,
    response parsing, and error handling. Provides access to specific API resource
    clients (e.g., ``studies``, ``sites``, ``records``) through properties.

    Authentication keys (``api_key``, ``security_key``) and ``base_url`` are typically
    read from environment variables (``IMEDNET_API_KEY``, ``IMEDNET_SECURITY_KEY``,
    ``IMEDNET_BASE_URL``) but can be provided explicitly during initialization.

    *Note: Resource clients like ``studies``, ``sites``, etc., are accessed via properties
    and documented individually.*
    """

    DEFAULT_BASE_URL = "https://edc.prod.imednetapi.com"

    # Add private attributes for caching resource clients
    _studies: Optional[StudiesClient] = None
    _sites: Optional[SitesClient] = None
    _forms: Optional[FormsClient] = None
    _intervals: Optional[IntervalsClient] = None
    _records: Optional[RecordsClient] = None
    _record_revisions: Optional[RecordRevisionsClient] = None
    _variables: Optional[VariablesClient] = None
    _codings: Optional[CodingsClient] = None
    _subjects: Optional[SubjectsClient] = None
    _users: Optional[UsersClient] = None
    _visits: Optional[VisitsClient] = None
    _jobs: Optional[JobsClient] = None

    def __init__(
        self,
        api_key: Optional[str] = None,
        security_key: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: TimeoutTypes = httpx.Timeout(30.0, connect=5.0),
        retries: int = 3,
        backoff_factor: float = 1,
        retry_methods: Optional[Set[str]] = None,
        retry_exceptions: Optional[Set[type]] = None,
    ):
        """Initializes the ImednetClient.

        Sets up the underlying HTTP client (``httpx.Client``), authentication headers,
        and retry logic based on provided parameters or environment variables.

        Args:
            api_key: Your iMednet API key. If None, reads from the
                ``IMEDNET_API_KEY`` environment variable.
            security_key: Your iMednet Security key. If None, reads from the
                ``IMEDNET_SECURITY_KEY`` environment variable.
            base_url: The base URL for the iMednet API instance (e.g.,
                ``https://your_instance.imednetapi.com``). If None, reads from
                ``IMEDNET_BASE_URL`` or defaults to the production URL.
            timeout: Default request timeout configuration. Can be a float (total
                timeout in seconds) or an ``httpx.Timeout`` object allowing separate
                connect, read, write, pool timeouts. Defaults to 30s total, 5s connect.
            retries: Maximum number of retry attempts for failed requests eligible for retry.
                Set to 0 to disable retries. Defaults to 3.
            backoff_factor: Multiplier for exponential backoff between retries. The delay
                is calculated as ``backoff_factor * (2 ** (attempt - 1))`` seconds.
                Used by ``tenacity.wait_exponential``. Defaults to 1.
            retry_methods: Set of uppercase HTTP methods (e.g., ``{"GET", "PUT"}``) to allow
                           retries for. Defaults to ``{"GET"}``.
            retry_exceptions: Set of exception types that trigger a retry attempt.
                              Defaults include various ``httpx`` network errors,
                              ``RateLimitError`` (429), and ``ApiError`` (5xx). User-provided
                              exceptions are added to this default set.

        Raises:
            ValueError: If ``api_key`` or ``security_key`` is not provided directly
                        and cannot be found in the corresponding environment variables.
        """
        self.base_url = base_url or self.DEFAULT_BASE_URL

        # Determine API Key: argument > environment variable > error
        resolved_api_key = api_key or os.getenv("IMEDNET_API_KEY")
        if not resolved_api_key:
            raise ValueError(
                "API key not provided and IMEDNET_API_KEY environment variable not set."
            )
        self._api_key = resolved_api_key

        # Determine Security Key: argument > environment variable > error
        resolved_security_key = security_key or os.getenv("IMEDNET_SECURITY_KEY")
        if not resolved_security_key:
            raise ValueError(
                "Security key not provided and IMEDNET_SECURITY_KEY environment variable not set."
            )
        self._security_key = resolved_security_key

        self._default_timeout = timeout
        self._retries = retries
        self._backoff_factor = backoff_factor  # Store for tenacity wait config
        self._retry_methods = retry_methods if retry_methods is not None else DEFAULT_RETRY_METHODS
        # Combine default and user-provided retry exceptions
        base_retry_exceptions = DEFAULT_RETRY_EXCEPTIONS.copy()
        if retry_exceptions:
            base_retry_exceptions.update(retry_exceptions)
        self._retry_exceptions_tuple = tuple(base_retry_exceptions)  # Tenacity needs a tuple

        self._default_headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "x-api-key": self._api_key,
            "x-imn-security-key": self._security_key,
        }

        self._client = httpx.Client(
            base_url=self.base_url,
            headers=self._default_headers,
            timeout=self._default_timeout,
        )

    def _make_request_attempt(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]],
        json_data: Optional[Any],  # Renamed from json to avoid conflict
        timeout: TimeoutTypes,  # Use the determined timeout
        **kwargs: Any,
    ) -> httpx.Response:
        """Makes a single HTTP request attempt. Called by the retry logic."""
        logger.debug(f"Making request: {method} {endpoint} Params: {params} Body: {json_data}")
        try:
            response = self._client.request(
                method,
                endpoint,
                params=params,
                json=json_data,  # Use the renamed variable
                timeout=timeout,  # Pass the specific timeout
                **kwargs,
            )
            # Raise HTTPStatusError for 4xx/5xx responses immediately after the request
            # This allows the retry logic (_should_retry) to catch specific SDK exceptions
            response.raise_for_status()
            return response
        except httpx.HTTPStatusError as e:
            # Convert httpx error to our custom SDK exception before retry check
            sdk_exception = self._handle_api_error(e.response, endpoint)
            logger.warning(
                f"Request attempt failed with status {e.response.status_code}. "
                f"Error: {sdk_exception}. Retrying if applicable..."
            )
            raise sdk_exception from e
        except httpx.RequestError as e:
            # Handle network/connection errors
            logger.warning(f"Request attempt failed with network error: {e}. Retrying if applicable...")
            raise  # Reraise httpx.RequestError for tenacity to catch

    def _request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        json: Optional[Any] = None,
        response_model: Optional[Union[Type[T], Type[List[T]]]] = None,
        timeout: Optional[TimeoutTypes] = None,  # Add timeout parameter
        **kwargs: Any,
    ) -> Union[T, List[T], httpx.Response]:
        """Core request method with retry logic, response parsing, and error handling.

        Handles making the actual HTTP request using the configured httpx client,
        applying retry logic via tenacity, parsing successful responses into
        Pydantic models (if specified), and raising appropriate SDK exceptions
        for API errors.

        Args:
            method: HTTP method (e.g., "GET", "POST").
            endpoint: API endpoint path (relative to base URL).
            params: Optional dictionary of query parameters.
            json: Optional request body payload (dict, list, or Pydantic model).
            response_model: Optional Pydantic model class or List[ModelClass] for parsing.
            timeout: Optional timeout override for this specific request.  # Add timeout to docstring
            **kwargs: Additional keyword arguments passed to httpx's request method.

        Returns:
            The deserialized Pydantic model(s) if response_model is provided and
            the request is successful (2xx status), otherwise the raw httpx.Response.

        Raises:
            ImednetSdkException: For API errors (4xx/5xx) or validation issues.
            httpx.RequestError: For underlying connection/network issues if retries fail.
            RetryError: If retries are exhausted.
        """
        # Determine the timeout for this specific request
        request_timeout = timeout if timeout is not None else self._default_timeout

        # Prepare retry configuration using tenacity
        retryer = Retrying(
            stop=stop_after_attempt(self._retries + 1),  # +1 because first attempt is not a retry
            wait=wait_exponential(multiplier=self._backoff_factor, min=1, max=10),
            reraise=True,  # Reraise the exception if retries fail
        )

        try:
            # Use tenacity's retry mechanism
            response = retryer(
                self._make_request_attempt,
                method=method,
                endpoint=endpoint,
                params=params,
                json_data=json,  # Pass renamed json_data
                timeout=request_timeout,
                **kwargs,
            )
        except RetryError as e:
            logger.error(f"Request failed after {self._retries} retries: {e}")
            # Reraise the last exception encountered during retries
            raise e.last_attempt.exception  # type: ignore

        # Process the final response (either successful or non-retried error)
        if response_model:
            try:
                adapter = TypeAdapter(response_model)
                return adapter.validate_python(response.json())
            except ValidationError as validation_exc:
                raise RuntimeError(
                    f"Failed to validate response data: {validation_exc}"
                ) from validation_exc
        return response

    def _handle_api_error(self, response: httpx.Response, request_path: str) -> None:
        """Parses API error responses and raises appropriate `ImednetSdkException` subclasses.

        Analyzes the HTTP status code and, if possible, the JSON error payload
        (following the standard iMednet error structure in `metadata.error`)
        to determine the most specific exception to raise.

        This method is called internally by `_make_request_attempt` when a non-2xx
        status code is received.

        Args:
            response: The `httpx.Response` object containing the error.
            request_path: The relative path of the API request that failed, used for context
                          in the raised exception.

        Raises:
            BadRequestError: For 400 errors (excluding specific validation errors).
            SdkValidationError: For 400 errors with API code "1000".
            AuthenticationError: For 401 errors.
            AuthorizationError: For 403 errors.
            NotFoundError: For 404 errors.
            RateLimitError: For 429 errors.
            ApiError: For 5xx errors or other unexpected 4xx errors.
            ImednetSdkException: As a fallback for unhandled status codes or if parsing fails
                                 unexpectedly.
        """
        status_code = response.status_code
        timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
        error_details: Dict[str, Any] = {}
        api_error_code: Optional[str] = None
        description: str = f"HTTP error {status_code} occurred."
        attribute: Optional[str] = None
        value: Optional[Any] = None

        try:
            error_data = response.json()
            metadata = error_data.get("metadata", {})
            error_info = metadata.get("error", {})

            api_error_code = error_info.get("code")
            # Prioritize 'message', fallback to 'description', then default
            description = error_info.get("message", error_info.get("description", description))
            attribute = error_info.get("attribute")
            value = error_info.get("value")
            error_details = error_data

        except ValueError:
            description = (
                f"HTTP error {status_code} occurred, and the response body was not valid JSON."
            )
            error_details = {"raw_response": response.text}

        exception_args = {
            "message": description,
            "status_code": status_code,
            "api_error_code": api_error_code,
            "request_path": request_path,
            "response_body": error_details,
            "timestamp": timestamp,
        }

        if status_code == 400:
            if api_error_code == "1000":
                raise SdkValidationError(**exception_args, attribute=attribute, value=value)
            else:
                raise BadRequestError(**exception_args)
        elif status_code == 401:
            raise AuthenticationError(**exception_args)
        elif status_code == 403:
            raise AuthorizationError(**exception_args)
        elif status_code == 404:
            raise NotFoundError(**exception_args)
        elif status_code == 429:
            raise RateLimitError(**exception_args)
        elif status_code >= 500:
            raise ApiError(**exception_args)
        elif status_code >= 400:
            raise ApiError(**exception_args)
        else:
            raise ImednetSdkException(
                f"Unhandled HTTP status code {status_code}.",
                status_code=status_code,
                request_path=request_path,
                response_body=error_details,
                timestamp=timestamp,
            )

    def _get(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        response_model: Optional[Union[Type[T], Type[List[T]]]] = None,
        timeout: TimeoutTypes = None,
        **kwargs: Any,
    ) -> Union[T, List[T], httpx.Response]:
        """Sends a GET request using the internal `_request` method.

        A convenience wrapper around `_request` for GET operations.

        Args:
            endpoint: The API endpoint path (relative to `base_url`).
            params: Optional dictionary of query parameters.
            response_model: Optional Pydantic model class (or `List[ModelClass]`)
                            to parse the successful JSON response into.
            timeout: Optional timeout configuration override for this request.
            **kwargs: Additional arguments passed directly to `_request`.

        Returns:
            The deserialized Pydantic model(s) or the raw `httpx.Response`,
            as returned by `_request`.

        Raises:
            Propagates exceptions raised by `_request`.
        """
        return self._request(
            "GET", endpoint, params=params, response_model=response_model, timeout=timeout, **kwargs
        )

    def _post(
        self,
        endpoint: str,
        json: Optional[Any] = None,
        response_model: Optional[Union[Type[T], Type[List[T]]]] = None,
        timeout: TimeoutTypes = None,
        **kwargs: Any,
    ) -> Union[T, List[T], httpx.Response]:
        """Sends a POST request using the internal `_request` method.

        A convenience wrapper around `_request` for POST operations.

        Args:
            endpoint: The API endpoint path (relative to `base_url`).
            json: Optional request body payload (dict, list, or Pydantic model).
            response_model: Optional Pydantic model class (or `List[ModelClass]`)
                            to parse the successful JSON response into.
            timeout: Optional timeout configuration override for this request.
            **kwargs: Additional arguments passed directly to `_request`.

        Returns:
            The deserialized Pydantic model(s) or the raw `httpx.Response`,
            as returned by `_request`.

        Raises:
            Propagates exceptions raised by `_request`.
        """
        return self._request(
            "POST", endpoint, json=json, response_model=response_model, timeout=timeout, **kwargs
        )

    def get_typed_records_for_subject(
        self,
        study_key: str,
        subject_key: str,
        form_key: str,
        record_model_name: Optional[str] = None,
        **kwargs: Any,
    ) -> List[BaseModel]:
        """Fetches records for a subject and dynamically parses them into a Pydantic model.

        Retrieves variable definitions for the specified form, generates a dynamic
        Pydantic model based on those variables, fetches the records for the subject,
        and parses the record data into instances of the generated model.

        Args:
            study_key: The key of the study.
            subject_key: The key of the subject.
            form_key: The key of the form containing the desired variables.
            record_model_name: Optional name for the dynamically created Pydantic model.
                               Defaults to f"{form_key.capitalize()}Record".
            **kwargs: Additional keyword arguments passed to the underlying
                      `records.list_records` call (e.g., `filter`, `page`, `size`).

        Returns:
            A list of Pydantic model instances, where each instance represents a record
            parsed according to the dynamically generated model based on the form's variables.

        Raises:
            ImednetSdkException: If fetching variables or records fails.
            RuntimeError: If the dynamic model cannot be created or data cannot be parsed.
        """
        # Use the imported utility function
        return _fetch_and_parse_typed_records(
            client=self,
            study_key=study_key,
            subject_key=subject_key,
            form_key=form_key,
            record_model_name=record_model_name,
            **kwargs, # Pass kwargs correctly
        )

    # --- Resource Client Properties ---
    @property
    def studies(self) -> StudiesClient:
        """Accessor for the Studies API resource client.

        Provides methods for interacting with study-related endpoints (e.g., listing studies).
        The client instance is cached upon first access.

        Returns:
            An instance of `StudiesClient` associated with this `ImednetClient`.
        """
        if self._studies is None:
            self._studies = StudiesClient(self)
        return self._studies

    @property
    def sites(self) -> SitesClient:
        """Accessor for the Sites API resource client.

        Provides methods for interacting with site-related endpoints (e.g., listing sites
        within a study). The client instance is cached upon first access.

        Returns:
            An instance of `SitesClient` associated with this `ImednetClient`.
        """
        if self._sites is None:
            self._sites = SitesClient(self)
        return self._sites

    @property
    def forms(self) -> FormsClient:
        """Accessor for the Forms API resource client.

        Provides methods for interacting with form definition endpoints (e.g., listing forms
        within a study). The client instance is cached upon first access.

        Returns:
            An instance of `FormsClient` associated with this `ImednetClient`.
        """
        if self._forms is None:
            self._forms = FormsClient(self)
        return self._forms

    @property
    def intervals(self) -> IntervalsClient:
        """Accessor for the Intervals API resource client.

        Provides methods for interacting with interval/visit definition endpoints.
        The client instance is cached upon first access.

        Returns:
            An instance of `IntervalsClient` associated with this `ImednetClient`.
        """
        if self._intervals is None:
            self._intervals = IntervalsClient(self)
        return self._intervals

    @property
    def records(self) -> RecordsClient:
        """Accessor for the Records API resource client.

        Provides methods for interacting with record data endpoints (e.g., listing,
        creating, updating records). The client instance is cached upon first access.

        Returns:
            An instance of `RecordsClient` associated with this `ImednetClient`.
        """
        if self._records is None:
            self._records = RecordsClient(self)
        return self._records

    @property
    def record_revisions(self) -> RecordRevisionsClient:
        """Accessor for the Record Revisions (Audit Trail) API resource client.

        Provides methods for interacting with record audit trail endpoints.
        The client instance is cached upon first access.

        Returns:
            An instance of `RecordRevisionsClient` associated with this `ImednetClient`.
        """
        if self._record_revisions is None:
            self._record_revisions = RecordRevisionsClient(self)
        return self._record_revisions

    @property
    def variables(self) -> VariablesClient:
        """Accessor for the Variables API resource client.

        Provides methods for interacting with variable definition endpoints (e.g., listing
        variables for a study or form). The client instance is cached upon first access.

        Returns:
            An instance of `VariablesClient` associated with this `ImednetClient`.
        """
        if self._variables is None:
            self._variables = VariablesClient(self)
        return self._variables

    @property
    def codings(self) -> CodingsClient:
        """Accessor for the Codings API resource client.

        Provides methods for interacting with coding data endpoints.
        The client instance is cached upon first access.

        Returns:
            An instance of `CodingsClient` associated with this `ImednetClient`.
        """
        if self._codings is None:
            self._codings = CodingsClient(self)
        return self._codings

    @property
    def subjects(self) -> SubjectsClient:
        """Accessor for the Subjects API resource client.

        Provides methods for interacting with subject data endpoints (e.g., listing subjects).
        The client instance is cached upon first access.

        Returns:
            An instance of `SubjectsClient` associated with this `ImednetClient`.
        """
        if self._subjects is None:
            self._subjects = SubjectsClient(self)
        return self._subjects

    @property
    def users(self) -> UsersClient:
        """Accessor for the Users API resource client.

        Provides methods for interacting with user data endpoints.
        The client instance is cached upon first access.

        Returns:
            An instance of `UsersClient` associated with this `ImednetClient`.
        """
        if self._users is None:
            self._users = UsersClient(self)
        return self._users

    @property
    def visits(self) -> VisitsClient:
        """Accessor for the Visits API resource client.

        Provides methods for interacting with subject visit instance endpoints.
        The client instance is cached upon first access.

        Returns:
            An instance of `VisitsClient` associated with this `ImednetClient`.
        """
        if self._visits is None:
            self._visits = VisitsClient(self)
        return self._visits

    @property
    def jobs(self) -> JobsClient:
        """Accessor for the Jobs API resource client.

        Provides methods for checking the status of asynchronous jobs.
        The client instance is cached upon first access.

        Returns:
            An instance of `JobsClient` associated with this `ImednetClient`.
        """
        if self._jobs is None:
            self._jobs = JobsClient(self)
        return self._jobs

    # --- Context Manager Methods ---
    def __enter__(self) -> "ImednetClient":
        """Allows the client to be used as a context manager."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Closes the client connection pool upon exiting the context manager block."""
        self.close()

    def close(self):
        """Closes the underlying `httpx.Client` connection pool.

        It's recommended to call this method when you are finished with the client,
        or use the client as a context manager (``with ImednetClient() as client: ...``)
        to ensure connections are properly released.
        """
        self._client.close()
        logger.info("iMednet client connection closed.")
