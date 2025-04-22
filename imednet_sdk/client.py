"""
Core HTTP client for interacting with the iMednet API.

This module defines the `ImednetClient`, the primary entry point for using the SDK.
It handles:

- Authentication using API and Security keys (read from arguments or environment variables).
- Configuration of base URL, timeouts, and retry logic.
- Making HTTP requests (GET, POST, PUT, DELETE) to the iMednet API.
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
from tenacity import (RetryError, retry, retry_if_exception, retry_if_exception_type,
                      stop_after_attempt, wait_exponential)

# Import resource clients
from .api import JobsClient  # Group API imports
from .api import (CodingsClient, FormsClient, IntervalsClient, QueriesClient, RecordRevisionsClient,
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
        url: str,
        params: Optional[Dict[str, Any]],
        request_json: Optional[Any],
        request_timeout: TimeoutTypes,
        response_model: Optional[Union[Type[T], Type[List[T]]]],
        **kwargs: Any,
    ) -> Union[T, List[T], httpx.Response]:
        """Executes a single HTTP request attempt and handles the response.

        Sends the request using the internal ``httpx.Client``. If the response
        indicates an API error (non-2xx status), it raises the appropriate
        ``ImednetSdkException`` subclass via ``_handle_api_error``. If successful
        and a ``response_model`` is provided, it attempts to parse the JSON
        response into the model, raising ``SdkValidationError`` on failure.

        Network-related errors (subclasses of ``httpx.RequestError``) are allowed
        to propagate up to be handled by the retry decorator.

        Args:
            method: The HTTP method (e.g., 'GET', 'POST').
            url: The target URL path for the request (relative to ``base_url``).
            params: Optional dictionary of query parameters.
            request_json: Optional JSON payload for the request body (typically a dict
                          or list, will be serialized by httpx).
            request_timeout: The timeout configuration for this specific attempt.
            response_model: Optional Pydantic model (or ``List[ModelType]``) to parse
                            the successful JSON response into.
            **kwargs: Additional keyword arguments passed directly to ``httpx.Client.request``
                      (e.g., ``headers``).

        Returns:
            If ``response_model`` is provided and the request/parsing is successful:
                An instance of the ``response_model`` (or a list of instances).
            If ``response_model`` is None and the request is successful:
                The raw ``httpx.Response`` object.

        Raises:
            AuthenticationError: For 401 Unauthorized errors.
            AuthorizationError: For 403 Forbidden errors.
            NotFoundError: For 404 Not Found errors.
            RateLimitError: For 429 Too Many Requests errors.
            ValidationError: For 400 Bad Request errors specifically identified as
                             validation issues (e.g., API code 1000).
            BadRequestError: For other 400 Bad Request errors.
            ApiError: For other 4xx or 5xx errors.
            SdkValidationError: If ``response_model`` is provided but the response JSON
                                cannot be parsed into the model.
            httpx.RequestError: For network-level issues (connection, timeout, etc.).
                                These are typically caught by the retry logic.
        """
        request_path = str(
            self._client.build_request(method, url, params=params, json=request_json).url
        )
        try:
            response = self._client.request(
                method=method,
                url=url,
                params=params,
                json=request_json,
                timeout=request_timeout,
                **kwargs,
            )

            # Check for non-2xx responses and raise custom exceptions
            if not response.is_success:
                self._handle_api_error(
                    response, request_path
                )  # This will raise appropriate exception

            # If successful and no response model, return raw response
            if response_model is None:
                return response

            # Decode and validate JSON if response_model is provided
            try:
                response_data = response.json()
            except ValueError as json_exc:
                raise RuntimeError(f"Failed to decode JSON response: {json_exc}") from json_exc

            try:
                adapter = TypeAdapter(response_model)
                validated_data = adapter.validate_python(response_data)
                return validated_data
            except ValidationError as validation_exc:
                raise RuntimeError(
                    f"Failed to validate response data: {validation_exc}"
                ) from validation_exc

        except httpx.RequestError as exc:
            # Re-raise network errors to be potentially caught by tenacity
            raise exc
        # Custom exceptions raised by _handle_api_error will also propagate up

    def _request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        json: Optional[Any] = None,
        response_model: Optional[Union[Type[T], Type[List[T]]]] = None,
        timeout: TimeoutTypes = None,
        **kwargs: Any,
    ) -> Union[T, List[T], httpx.Response]:
        """Makes an HTTP request with retry logic and response handling.

        This is the core method used by `_get`, `_post`, etc., and by the resource
        clients. It orchestrates the request lifecycle:

        1. **Prepares Request:** Determines the full URL and timeout.
        2. **Serializes Payload:** Converts Pydantic models in the `json` argument
           to dictionaries suitable for `httpx`.
        3. **Applies Retries:** Uses the `tenacity` library to wrap the actual
           request attempt (`_make_request_attempt`). Retries are performed based
           on the configured `retries`, `backoff_factor`, `retry_methods`, and
           `retry_exceptions`.
        4. **Returns Result:** Returns the processed response (deserialized model
           or raw `httpx.Response`) from the final successful attempt, or re-raises
           the exception if retries are exhausted.

        Args:
            method: The HTTP method (e.g., 'GET', 'POST').
            endpoint: The API endpoint path (relative to the client's `base_url`).
            params: Optional dictionary of query parameters.
            json: Optional request body payload. Can be a dictionary, list, or a
                  Pydantic model instance (which will be serialized).
            response_model: Optional Pydantic model class (or `List[ModelClass]`)
                            to parse the successful JSON response into.
            timeout: Optional timeout configuration for this specific request,
                     overriding the client's default `_default_timeout`.
            **kwargs: Additional keyword arguments passed down to `_make_request_attempt`
                      and subsequently to `httpx.Client.request` (e.g., `headers`).

        Returns:
            The result from `_make_request_attempt` after applying retry logic:
            - An instance or list of `response_model` if provided and successful.
            - The raw `httpx.Response` object if `response_model` is None and successful.

        Raises:
            ImednetSdkException: Or its subclasses, if the API returns an error status
                                 code after exhausting retries.
            httpx.RequestError: If a network-level error occurs after exhausting retries.
            RuntimeError: If JSON decoding or Pydantic validation fails.
            RetryError: If retries are exhausted (though this is typically caught and
                        the underlying cause is re-raised).
        """
        url = endpoint
        request_timeout = timeout if timeout is not None else self._default_timeout

        # Handle potential Pydantic model serialization for request body
        request_json = None
        if isinstance(json, BaseModel):
            # Serialize Pydantic model to dict using aliases
            request_json = json.model_dump(by_alias=True, mode="json")
        elif json is not None:
            request_json = json  # Assume it's already a dict/serializable

        # --- Tenacity Retry Logic ---
        # Check if the method is configured for retries
        if method.upper() in self._retry_methods:
            # Define the retry decorator dynamically
            retry_decorator = retry(
                stop=stop_after_attempt(self._retries + 1),  # Total attempts = initial + retries
                wait=wait_exponential(
                    multiplier=self._backoff_factor, min=0.5, max=10
                ),  # Exponential backoff with jitter
                retry=retry_if_exception_type(
                    self._retry_exceptions_tuple
                ),  # Retry only on specific exceptions
                reraise=True,  # Reraise the last exception after exhausting attempts
            )
            # Apply the decorator to the request attempt function
            try:
                return retry_decorator(self._make_request_attempt)(
                    method=method,
                    url=url,
                    params=params,
                    request_json=request_json,
                    request_timeout=request_timeout,
                    response_model=response_model,
                    **kwargs,
                )
            except RetryError as e:
                # If tenacity fails, reraise the underlying cause
                raise e.cause from e
        else:
            # If method is not retryable, make a single attempt directly
            return self._make_request_attempt(
                method=method,
                url=url,
                params=params,
                request_json=request_json,
                request_timeout=request_timeout,
                response_model=response_model,
                **kwargs,
            )

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
            description = error_info.get(
                "description", description
            )
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

    def get_typed_records(
        self, study_key: str, form_key: str, **kwargs
    ) -> List[BaseModel]:
        """Fetches records for a form and parses `recordData` into dynamic Pydantic models.

        This method provides a way to get strongly-typed access to the data within
        `recordData` fields, based on the variable definitions (type, name) associated
        with the specified `form_key`.

        It performs the following steps:

        1. Fetches variable definitions for the `form_key` using `self.variables.list_variables`.

        2. Dynamically builds a Pydantic model based on these variable definitions.

        3. Fetches records for the `form_key` using `self.records.list_records` (handling pagination).

        4. For each fetched record, validates and parses its `recordData` using the dynamically
           created Pydantic model.

        5. Returns a list of these dynamic Pydantic model instances.

        Args:
            study_key: The key identifying the study.

            form_key: The key identifying the form whose records and variables are needed.

            **kwargs: Additional keyword arguments passed to the underlying
                      `self.records.list_records` call (e.g., `filter`, `sort`, `size`,
                      `page`, `record_data_filter`). Pagination arguments (`page`, `size`)
                      are handled internally to fetch all records matching the criteria.

        Returns:
            A list of dynamically created Pydantic model instances, each representing
            the validated `recordData` of a fetched record for the specified form.
            Returns an empty list if no variables are found for the form or if
            no records match the criteria.

        Raises:
            ImednetSdkException: If fetching variables or records fails due to API errors.

            ValueError: If building the dynamic model fails (e.g., missing `variableName`).

            RuntimeError: If JSON decoding or Pydantic validation fails during processing.
        """
        return _fetch_and_parse_typed_records(
            variables_client=self.variables,
            records_client=self.records,
            study_key=study_key,
            form_key=form_key,
            **kwargs,
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

        Provides methods for interacting with asynchronous job status endpoints.
        The client instance is cached upon first access.

        Returns:
            An instance of `JobsClient` associated with this `ImednetClient`.
        """
        if self._jobs is None:
            self._jobs = JobsClient(self)
        return self._jobs

    # --- End Resource Client Properties ---

    def close(self):
        """Closes the underlying `httpx.Client` connection pool.

        It's recommended to call this method when you are finished with the client,
        or use the client as a context manager (`with ImednetClient() as client:`)
        which handles closing automatically.
        """
        self._client.close()

    def __enter__(self) -> "ImednetClient":
        """Enables the use of the client as a context manager.

        Returns:
            The client instance itself.
        """
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Closes the client connection pool upon exiting the context manager block."""
        self.close()
