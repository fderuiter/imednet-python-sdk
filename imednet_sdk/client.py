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

    # Client uses environment variables IMEDNET_API_KEY, IMEDNET_SECURITY_KEY, IMEDNET_BASE_URL by default\r
    client = ImednetClient()\r
\r
    try:\r
        response = client.studies.list_studies(size=10)\r
        if response and response.data:\r
            for study in response.data:\r
                print(f"Study: {study.studyName} (Key: {study.studyKey})")\r
    except ImednetSdkException as e:\r
        print(f"API Error: {e}")\r
\r
This module is part of the iMednet SDK, designed for seamless interaction with the iMednet\r
API, enabling efficient data management and retrieval for clinical studies.\r
"""

import json  # Import the standard json library
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
from .api import (
    CodingsClient,
    FormsClient,
    IntervalsClient,
    JobsClient,
    RecordRevisionsClient,
    RecordsClient,
    SitesClient,
    StudiesClient,
    SubjectsClient,
    UsersClient,
    VariablesClient,
    VisitsClient,
)

# Import custom exceptions
from .exceptions import (
    ApiError,
    AuthenticationError,
    AuthorizationError,
    BadRequestError,
    ImednetSdkException,
    NotFoundError,
    RateLimitError,
)
from .exceptions import ValidationError as SdkValidationError  # Alias to avoid name clash

# Import the new helper function
from .utils import _fetch_and_parse_typed_records  # Import build_model_from_variables
from .utils import build_model_from_variables

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
    # RateLimitError, # REMOVED: Do not retry 429 by default
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
        retry_on_status_codes: Optional[Set[int]] = None,  # Added for more control if needed later
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
        # Ensure 4xx errors are NOT retried by default unless explicitly added
        self._retry_exceptions_tuple = tuple(
            exc
            for exc in base_retry_exceptions
            if not issubclass(
                exc,
                (
                    BadRequestError,  # Includes SdkValidationError
                    AuthenticationError,
                    AuthorizationError,
                    NotFoundError,
                    RateLimitError,
                ),
            )
        )

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

        # Handle Pydantic model serialization before sending
        if isinstance(json_data, BaseModel):
            processed_json_data = json_data.model_dump(by_alias=True, mode="json")
        else:
            processed_json_data = json_data

        try:
            response = self._client.request(
                method,
                endpoint,
                params=params,
                json=processed_json_data,  # Use processed data
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
            logger.warning(
                f"Request attempt failed with network error: {e}. Retrying if applicable..."
            )
            raise  # Reraise httpx.RequestError for tenacity to catch

    def _request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        json: Optional[Any] = None,  # Keep original name 'json' for public-facing methods
        response_model: Optional[Union[Type[T], Type[List[T]]]] = None,
        timeout: Optional[TimeoutTypes] = None,
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
            RuntimeError: If JSON decoding or Pydantic validation fails.
        """
        # Determine the timeout for this specific request
        request_timeout = timeout if timeout is not None else self._default_timeout

        # Prepare retry configuration using tenacity
        retryer = Retrying(
            stop=stop_after_attempt(self._retries + 1),  # +1 because first attempt is not a retry
            wait=wait_exponential(multiplier=self._backoff_factor, min=1, max=10),
            retry=(
                lambda retry_state: isinstance(
                    retry_state.outcome.exception(), self._retry_exceptions_tuple
                )
            ),  # Retry only on specific exceptions
            reraise=True,  # Reraise the exception if retries fail
        )

        try:
            # Use tenacity's retry mechanism
            response = retryer(
                self._make_request_attempt,
                method=method,
                endpoint=endpoint,
                params=params,
                json_data=json,  # Pass original json data (make_request_attempt handles serialization)
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
                response_json = response.json()
            except json.JSONDecodeError as decode_exc:
                logger.error(
                    f"Failed to decode JSON response from {method} {endpoint}: {decode_exc}"
                )
                raise RuntimeError(
                    f"Failed to decode JSON response from {method} {endpoint}. "
                    f"Response text: {response.text[:500]}..."
                ) from decode_exc

            try:
                # Use model_validate for Pydantic v2
                if hasattr(response_model, "model_validate"):
                    adapter = TypeAdapter(response_model)
                    return adapter.validate_python(response_json)
                else:  # Fallback for older Pydantic or different structure
                    # This part might need adjustment based on exact Pydantic version/usage
                    if (
                        isinstance(response_json, list)
                        and hasattr(response_model, "__args__")
                        and response_model.__args__
                    ):
                        item_model = response_model.__args__[0]
                        return [item_model.parse_obj(item) for item in response_json]
                    elif isinstance(response_model, type) and issubclass(response_model, BaseModel):
                        return response_model.parse_obj(response_json)
                    else:
                        # If response_model is not a standard Pydantic type/list, return raw JSON
                        logger.warning(
                            f"Unsupported response_model type: {type(response_model)}. "
                            f"Returning raw JSON."
                        )
                        return response_json  # Or raise error?

            except ValidationError as validation_exc:
                logger.error(
                    f"Failed to validate response data for {method} {endpoint}: {validation_exc}"
                )
                raise RuntimeError(
                    f"Failed to validate response data: {validation_exc}"
                ) from validation_exc
            except Exception as e:  # Catch other potential validation/parsing errors
                logger.error(
                    f"Unexpected error during response parsing for {method} {endpoint}: {e}"
                )
                raise RuntimeError(f"Unexpected error during response parsing: {e}") from e

        return response  # Return raw response if no model specified

    def _handle_api_error(
        self, response: httpx.Response, request_path: str
    ) -> ImednetSdkException:  # Return type hint added
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
            ApiError: For 5xx errors.
            ImednetSdkException: For other unexpected errors or if the error payload
                                 cannot be parsed.
        """
        status_code = response.status_code
        try:
            # Attempt to parse the standard iMednet error structure
            error_data = response.json()
            metadata = error_data.get("metadata", {})
            error_info = metadata.get("error", {})
            api_error_code = error_info.get("code")
            message = error_info.get("message", "No error message provided.")
            details = error_info.get("details")
        except json.JSONDecodeError:
            # If JSON parsing fails, use the raw response text
            api_error_code = None
            message = f"API request failed with status {status_code}. Response body not valid JSON."
            details = response.text[:500]  # Include start of response text
        except Exception as e:
            # Catch any other unexpected errors during parsing
            api_error_code = None
            message = f"Unexpected error parsing API error response: {e}"
            details = response.text[:500]

        # Map status codes and API codes to specific exceptions
        exception_args = {
            "status_code": status_code,
            "api_error_code": api_error_code,
            "message": message,
            "details": details,
            "response_body": response.text,  # Always include the raw response body
            "request_path": request_path,
        }

        if status_code == 400:
            # Check for specific validation error code (e.g., "1000")
            if api_error_code == "1000":
                return SdkValidationError(**exception_args)
            return BadRequestError(**exception_args)
        elif status_code == 401:
            return AuthenticationError(**exception_args)
        elif status_code == 403:
            return AuthorizationError(**exception_args)
        elif status_code == 404:
            return NotFoundError(**exception_args)
        elif status_code == 429:
            return RateLimitError(**exception_args)
        elif status_code >= 500:
            return ApiError(**exception_args)
        else:
            # Fallback for unexpected status codes
            logger.warning(f"Received unexpected HTTP status code: {status_code}")
            return ImednetSdkException(**exception_args)

    # --- Resource Client Properties ---
    # Use properties to lazily initialize resource clients

    @property
    def studies(self) -> StudiesClient:
        """Access the Studies API resource client."""
        if self._studies is None:
            self._studies = StudiesClient(self)
        return self._studies

    @property
    def sites(self) -> SitesClient:
        """Access the Sites API resource client."""
        if self._sites is None:
            self._sites = SitesClient(self)
        return self._sites

    @property
    def forms(self) -> FormsClient:
        """Access the Forms API resource client."""
        if self._forms is None:
            self._forms = FormsClient(self)
        return self._forms

    @property
    def intervals(self) -> IntervalsClient:
        """Access the Intervals API resource client."""
        if self._intervals is None:
            self._intervals = IntervalsClient(self)
        return self._intervals

    @property
    def records(self) -> RecordsClient:
        """Access the Records API resource client."""
        if self._records is None:
            self._records = RecordsClient(self)
        return self._records

    @property
    def record_revisions(self) -> RecordRevisionsClient:
        """Access the Record Revisions API resource client."""
        if self._record_revisions is None:
            self._record_revisions = RecordRevisionsClient(self)
        return self._record_revisions

    @property
    def variables(self) -> VariablesClient:
        """Access the Variables API resource client."""
        if self._variables is None:
            self._variables = VariablesClient(self)
        return self._variables

    @property
    def codings(self) -> CodingsClient:
        """Access the Codings API resource client."""
        if self._codings is None:
            self._codings = CodingsClient(self)
        return self._codings

    @property
    def subjects(self) -> SubjectsClient:
        """Access the Subjects API resource client."""
        if self._subjects is None:
            self._subjects = SubjectsClient(self)
        return self._subjects

    @property
    def users(self) -> UsersClient:
        """Access the Users API resource client."""
        if self._users is None:
            self._users = UsersClient(self)
        return self._users

    @property
    def visits(self) -> VisitsClient:
        """Access the Visits API resource client."""
        if self._visits is None:
            self._visits = VisitsClient(self)
        return self._visits

    @property
    def jobs(self) -> JobsClient:
        """Access the Jobs API resource client."""
        if self._jobs is None:
            self._jobs = JobsClient(self)
        return self._jobs

    # --- Helper Methods ---
    def build_dynamic_record_model(
        self, study_key: str, form_key: str, **kwargs: Any
    ) -> Type[BaseModel]:
        """Dynamically builds a Pydantic model for a specific form's record data.

        Fetches the variable definitions for the given form and study, then constructs
        a Pydantic model with fields corresponding to those variables.

        Args:
            study_key: The key of the study.
            form_key: The key of the form.
            **kwargs: Additional arguments passed to the underlying `list_variables` call
                      (e.g., `page`, `size`).

        Returns:
            A dynamically created Pydantic `BaseModel` subclass representing the form's structure.

        Raises:
            ImednetSdkException: If fetching variables fails.
            RuntimeError: If model creation fails.
        """
        return build_model_from_variables(self, study_key, form_key, **kwargs)

    def fetch_and_parse_typed_records(
        self, study_key: str, form_key: str, **kwargs: Any
    ) -> ApiResponse[List[BaseModel]]:
        """Fetches records for a specific form and parses them using a dynamically built model.

        Combines `build_dynamic_record_model` and `records.list_records` to provide
        strongly-typed record data.

        Args:
            study_key: The key of the study.
            form_key: The key of the form.
            **kwargs: Additional arguments passed to the underlying `list_records` call
                      (e.g., `filter`, `page`, `size`, `sort`).

        Returns:
            An `ApiResponse` where the `data` attribute contains a list of dynamically
            typed Pydantic models representing the fetched records.

        Raises:
            ImednetSdkException: If fetching variables or records fails.
            RuntimeError: If model creation or parsing fails.
        """
        return _fetch_and_parse_typed_records(self, study_key, form_key, **kwargs)

    def close(self) -> None:
        """Closes the underlying HTTP client connection."""
        self._client.close()

    def __enter__(self) -> "ImednetClient":
        """Enter the runtime context related to this object."""
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Exit the runtime context related to this object."""
        self.close()
