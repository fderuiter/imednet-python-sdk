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

    # Client uses environment variables IMEDNET_API_KEY,
    # IMEDNET_SECURITY_KEY, IMEDNET_BASE_URL by default\r
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

import json as std_json
import logging
import os
from typing import Any, Dict, List, Optional, Set, Type, TypeVar, Union

import httpx
from pydantic import BaseModel, TypeAdapter, ValidationError

# Import tenacity for retry logic
from tenacity import RetryCallState, RetryError, Retrying, stop_after_attempt, wait_exponential

# Import resource clients
from imednet_sdk.api import (
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
from imednet_sdk.exceptions import (
    ApiError,
    AuthenticationError,
    AuthorizationError,
    BadRequestError,
    ImednetSdkException,
    NotFoundError,
    RateLimitError,
    SdkValidationError,
)

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

    def _extract_error_details(self, response: httpx.Response) -> Dict[str, Any]:
        """Extracts common error details from an httpx.Response."""
        details = {
            "message": f"API Error {response.status_code}",
            "status_code": response.status_code,
            "api_error_code": None,
            "request_path": str(response.request.url) if response.request else None,
            "response_body": None,
            "timestamp": None,
        }
        try:
            response_data = response.json()
            details["response_body"] = response_data
            # Attempt to extract common fields, adapt based on actual API error structure
            details["message"] = response_data.get("message", details["message"])
            # Check common keys for API error code
            details["api_error_code"] = (
                str(response_data.get("code", response_data.get("errorCode")))
                if response_data.get("code") or response_data.get("errorCode")
                else None
            )
            details["timestamp"] = response_data.get("timestamp")
        except std_json.JSONDecodeError:
            logger.warning(
                f"Failed to decode JSON error response for {details['request_path']}. "
                f"Body: {response.text[:200]}"
            )
            details["message"] = (
                f"API Error {response.status_code}: Failed to decode JSON response."
            )
            details["response_body"] = {"raw_text": response.text}
        except Exception:  # Catch other potential issues during extraction
            logger.warning("Failed to fully parse error response body.", exc_info=True)
            if not details["response_body"]:  # Ensure response_body is set if json() failed earlier
                details["response_body"] = {"raw_text": response.text}

        # Ensure message is set even if extraction fails partially
        if not details["message"]:
            details["message"] = f"API Error {response.status_code}"

        return details

    def _should_retry(self, retry_state: "RetryCallState") -> bool:
        """
        Determines if a request should be retried based on the outcome.

        Used by `tenacity.Retrying` as the `retry` condition.

        Args:
            retry_state: The state object provided by tenacity, containing
                         information about the attempt, outcome, etc

        Returns:
            True if the request should be retried, False otherwise.
        """
        # Don't retry if max attempts reached (handled by stop condition, but good practice)
        if retry_state.attempt_number >= self._retries + 1:
            return False

        outcome = retry_state.outcome
        # Only retry on specific exceptions
        if (
            outcome
            and outcome.failed
            and isinstance(outcome.exception(), self._retry_exceptions_tuple)
        ):
            # Check if the request method is in the allowed retry methods
            # The request object should be available in the exception context if it's an httpx error
            request = getattr(outcome.exception(), "request", None)
            if request and request.method in self._retry_methods:
                logger.info(
                    f"Retrying request {request.method} {request.url} "
                    f"(Attempt {retry_state.attempt_number}/{self._retries}) "
                    f"due to error: {outcome.exception().__class__.__name__}"
                )
                return True
            elif not request:
                # If we can't determine the method, retry based on exception only (conservative)
                logger.warning(
                    f"Retrying request (method unknown) "
                    f"(Attempt {retry_state.attempt_number}/{self._retries}) "
                    f"due to error: {outcome.exception().__class__.__name__}"
                )
                return True  # Or decide based on your policy if method is unknown

        # Log why we are not retrying if it's an exception we caught
        if outcome and outcome.failed:
            exc = outcome.exception()
            request = getattr(exc, "request", None)
            method = request.method if request else "Unknown Method"
            reason = "exception type not retryable"
            if (
                isinstance(exc, self._retry_exceptions_tuple)
                and request
                and method not in self._retry_methods
            ):
                reason = f"method '{method}' not in retryable methods"

            logger.debug(
                f"Not retrying request (Attempt {retry_state.attempt_number}) - Reason: {reason} "
                f"Error: {exc.__class__.__name__}"
            )

        return False

    def _build_url(self, path: str) -> str:
        """Constructs the full URL for an API endpoint.

        Ensures that there is exactly one slash between the base URL and the path.

        Args:
            path: The relative path of the API endpoint.

        Returns:
            The complete URL string.
        """
        # Ensure base_url ends with a slash and path doesn't start with one
        base = self.base_url.rstrip("/")
        path = path.lstrip("/")
        return f"{base}/{path}"

    def _prepare_headers(self, custom_headers: Optional[Dict[str, str]] = None) -> Dict[str, str]:
        """Merges default headers with custom headers provided for a specific request.

        Args:
            custom_headers: Optional dictionary of custom headers for the request.

        Returns:
            A dictionary containing the final headers for the request.
        """
        headers = self._default_headers.copy()
        if custom_headers:
            headers.update(custom_headers)
        # Ensure Content-Type is set correctly if not overridden
        if "Content-Type" not in headers:
            headers["Content-Type"] = "application/json"  # Default if missing
        return headers

    def _request(
        self,
        method: str,
        path: str,
        response_model: Optional[Type[T]] = None,
        *,
        params: Optional[Dict[str, Any]] = None,
        json: Optional[Any] = None,
        data: Optional[Dict[str, Any]] = None,
        files: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[TimeoutTypes] = None,
        allow_redirects: bool = True,
        **kwargs: Any,
    ) -> Optional[T]:
        """
        Internal method to make an HTTP request with retry logic.

        Args:
            method: HTTP method (e.g., "GET", "POST").
            path: API endpoint path (relative to base_url).
            response_model: Pydantic model to parse the successful response into.
            params: URL query parameters.
            json: Request body (JSON serializable).
            data: Request body (form data).
            files: Files to upload.
            headers: Custom request headers.
            timeout: Request timeout configuration.
            allow_redirects: Whether to follow redirects.
            **kwargs: Additional arguments passed to httpx.request.

        Returns:
            Parsed response model instance or None if response_model is None.

        Raises:
            ImednetSdkException: For API errors or validation issues.
            RetryError: If retries are exhausted.
        """
        # Prepare retry configuration using tenacity
        retryer = Retrying(
            stop=stop_after_attempt(self._retries),
            wait=wait_exponential(
                multiplier=self._backoff_factor, min=1, max=10
            ),  # Use backoff_factor
            retry=self._should_retry,  # Use the instance method
            reraise=True,
        )

        request_kwargs = {
            "method": method,
            "url": self._build_url(path),  # Use the new helper method
            "params": params,
            "json": json,
            "data": data,
            "files": files,
            "headers": self._prepare_headers(headers),  # Use the new helper method
            "timeout": (
                timeout if timeout is not None else self._default_timeout
            ),  # Use _default_timeout
            "follow_redirects": allow_redirects,
            **kwargs,
        }

        try:
            # Wrap the request attempt call in the retryer
            # Pass request_kwargs explicitly to the target function
            response = retryer(
                self._make_request_attempt, request_kwargs=request_kwargs
            )  # Pass kwargs correctly

            # Process successful response
            return self._handle_successful_response(response, response_model)

        except RetryError as e:
            logger.error(f"Request failed after {self._retries} retries: {e}")
            # The last exception raised during retries is available in e.cause
            if isinstance(e.cause, ImednetSdkException):
                raise e.cause  # Reraise the specific SDK exception
            elif isinstance(e.cause, httpx.RequestError):
                # Extract details primarily from the request if available
                request = e.cause.request
                raise ImednetSdkException(
                    message=f"Network error after retries: {e.cause}",
                    request_path=str(request.url) if request else None,
                    # No response available here, so status_code/response_body are None
                ) from e.cause
            else:
                # For other unexpected errors wrapped by RetryError
                raise ImednetSdkException(
                    f"An unexpected error occurred after retries: {e.cause}"
                ) from e.cause
        except ImednetSdkException:
            # Reraise SDK exceptions that were not retried or occurred on the first try
            raise
        except Exception as e:
            # Catch any other unexpected errors during the request process
            logger.exception(f"Unexpected error during request to {path}: {e}")
            # Cannot reliably get response details here
            raise ImednetSdkException(f"An unexpected error occurred: {e}") from e

    def _make_request_attempt(self, request_kwargs: Dict[str, Any]) -> httpx.Response:
        """
        Makes a single HTTP request attempt. Separated for retry logic.

        Args:
            request_kwargs: Dictionary containing all arguments for httpx.request.

        Returns:
            The httpx.Response object.

        Raises:
            httpx.RequestError: For connection errors, timeouts, etc.
            ImednetSdkException: For API errors (4xx/5xx).
        """
        logger.debug(f"Making request: {request_kwargs['method']} {request_kwargs['url']}")
        logger.debug(f"Params: {request_kwargs.get('params')} Body: {request_kwargs.get('json')}")
        try:
            response = self._client.request(**request_kwargs)
            response.raise_for_status()  # Raise HTTPStatusError for 4xx/5xx
            logger.debug(f"Request successful: {response.status_code} {response.url}")
            return response
        except httpx.HTTPStatusError as e:
            # Handle API errors (4xx/5xx)
            logger.warning(
                f"API Error: {e.response.status_code} for {e.request.method} {e.request.url}"
                f" Response: {e.response.text[:500]}"  # Log truncated response
            )
            # Extract details from the response
            error_details = self._extract_error_details(e.response)

            # Raise specific exceptions based on status code, passing extracted details
            if e.response.status_code == 400:
                raise BadRequestError(**error_details) from e
            elif e.response.status_code == 401:
                raise AuthenticationError(**error_details) from e
            elif e.response.status_code == 403:
                raise AuthorizationError(**error_details) from e
            elif e.response.status_code == 404:
                raise NotFoundError(**error_details) from e
            elif e.response.status_code == 429:
                raise RateLimitError(**error_details) from e
            elif 500 <= e.response.status_code < 600:
                # Raise generic ApiError for 5xx
                raise ApiError(**error_details) from e
            else:
                # Raise generic ApiError for other unexpected 4xx/5xx errors
                raise ApiError(**error_details) from e
        except httpx.RequestError as e:
            # Handle network errors (ConnectError, ReadTimeout, etc.)
            logger.warning(
                f"Network Error: {e.__class__.__name__} for {e.request.method} {e.request.url}"
            )
            raise  # Reraise network errors for tenacity to potentially retry

    def _handle_successful_response(
        self, response: httpx.Response, response_model: Optional[Type[T]]
    ) -> Optional[T]:
        """Handles successful HTTP responses (2xx status codes).

        Parses the JSON response body into the specified Pydantic model.

        Args:
            response: The successful `httpx.Response` object.
            response_model: The Pydantic model type to parse the response into.
                            If None, returns None.

        Returns:
            An instance of the `response_model` populated with data, or None.

        Raises:
            SdkValidationError: If the response body is not valid JSON or does not
                                conform to the `response_model` schema.
            ImednetSdkException: For other unexpected errors during parsing.
        """
        if response_model is None:
            return None

        try:
            # Check if content-type indicates JSON before attempting to parse
            content_type = response.headers.get("content-type", "").lower()
            if "application/json" not in content_type:
                # Handle non-JSON responses if necessary, or raise an error
                # For now, assume JSON is expected if a model is provided
                logger.warning(
                    f"Received non-JSON response (Content-Type: {content_type}) "
                    f"for {response.request.method} {response.request.url} "
                    f"when a response model was expected."
                )
                # Depending on strictness, you might raise SdkValidationError here
                # or return None, or try parsing anyway if the server sometimes omits Content-Type
                # Let's try parsing but log a warning.
                # If parsing fails below, SdkValidationError will be raised.

            response_data = response.json()

            # Use TypeAdapter for robust parsing, especially for list responses
            adapter = TypeAdapter(response_model)
            parsed_response = adapter.validate_python(response_data)
            logger.debug(
                f"Successfully parsed response for {response.request.method} "
                f"{response.request.url} into {response_model.__name__}"
            )
            return parsed_response

        except std_json.JSONDecodeError as e:
            logger.error(
                f"Failed to decode JSON response from {response.request.method} "
                f"{response.request.url}. Status: {response.status_code}. "
                f"Response text: {response.text[:500]}"  # Log truncated text
            )
            # Extract details, response_body will contain raw text
            error_details = self._extract_error_details(response)
            raise SdkValidationError(
                message=f"Invalid JSON received from API: {e}",
                status_code=error_details["status_code"],
                request_path=error_details["request_path"],
                response_body=error_details["response_body"],  # Contains raw text here
            ) from e
        except ValidationError as e:
            logger.error(
                f"Response validation failed for {response_model.__name__} from "
                f"{response.request.method} {response.request.url}. Errors: {e.errors()}"
                f" Raw Response: {response.text[:500]}"  # Log truncated text
            )
            # Extract details, response_body will contain the parsed (but invalid) JSON
            error_details = self._extract_error_details(response)
            # Construct a detailed message including validation errors
            validation_error_summary = str(e.errors())
            message = (
                f"API response did not match expected format ({response_model.__name__}): "
                f"{validation_error_summary[:200]}..."
                # Truncate validation errors in message
            )
            raise SdkValidationError(
                message=message,
                status_code=error_details["status_code"],
                request_path=error_details["request_path"],
                response_body=error_details["response_body"],
                # Note: SdkValidationError doesn't have a dedicated validation_errors field
                # Consider adding one or logging e.errors() separately if needed.
            ) from e
        except Exception as e:
            # Catch any other unexpected errors during response handling
            logger.exception(
                f"Unexpected error handling response from {response.request.method} "
                f"{response.request.url}: {e}"
            )
            # Try to extract details if a response object is available
            error_details = self._extract_error_details(response) if response else {}
            raise ImednetSdkException(
                message=f"An unexpected error occurred while processing the response: {e}",
                status_code=error_details.get("status_code"),
                request_path=error_details.get("request_path"),
                response_body=error_details.get("response_body"),
            ) from e

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

    # --- Core Request Methods ---
    def _get(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        response_model: Optional[Union[Type[T], Type[List[T]]]] = None,
        timeout: Optional[TimeoutTypes] = None,
        **kwargs: Any,
    ) -> Union[T, List[T], httpx.Response]:
        """Internal helper for making GET requests."""
        return self._request(
            "GET",
            endpoint,
            params=params,
            response_model=response_model,
            timeout=timeout,
            **kwargs,
        )

    def _post(
        self,
        endpoint: str,
        json: Optional[Any] = None,
        params: Optional[Dict[str, Any]] = None,
        response_model: Optional[Union[Type[T], Type[List[T]]]] = None,
        timeout: Optional[TimeoutTypes] = None,
        **kwargs: Any,
    ) -> Union[T, List[T], httpx.Response]:
        """Internal helper for making POST requests."""
        return self._request(
            "POST",
            endpoint,
            params=params,
            json=json,
            response_model=response_model,
            timeout=timeout,
            **kwargs,
        )

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
        # 1. Fetch variables using the variables client
        try:
            variables_response = self.variables.list_variables(
                study_key, filter=f"formKey=={form_key}", **kwargs
            )
            vars_meta_list = variables_response.data
            if not vars_meta_list:
                logger.warning(
                    f"No variables found for study '{study_key}', form '{form_key}'. "
                    f"Cannot create typed model."
                )
                # Return a base model if no variables found? Or raise?
                # For now, let's raise an error as the function expects to return a model.
                raise RuntimeError(
                    f"No variables found for form '{form_key}' in study '{study_key}'."
                )

            # Convert Pydantic models (if they are) to dicts
            vars_meta_dict = [v.model_dump(by_alias=False) for v in vars_meta_list]

        except ImednetSdkException as e:
            logger.error(
                f"Failed to fetch variables for study '{study_key}', form '{form_key}': {e}"
            )
            raise  # Re-raise the SDK exception
        except Exception as e:
            logger.error(f"Unexpected error fetching variables for form '{form_key}': {e}")
            raise ImednetSdkException(f"Unexpected error fetching variables: {e}") from e

        # 2. Build the model using the utility function
        model_name = f"{form_key.replace(' ', '_').capitalize()}RecordData"
        try:
            return build_model_from_variables(vars_meta_dict, model_name=model_name)
        except ValueError as e:
            logger.error(f"Failed to build dynamic model '{model_name}' for form '{form_key}': {e}")
            raise  # Re-raise the ValueError
        except Exception as e:
            logger.error(f"Unexpected error building dynamic model for form '{form_key}': {e}")
            raise ImednetSdkException(f"Unexpected error building dynamic model: {e}") from e

    def get_typed_records(  # Renamed from fetch_and_parse_typed_records
        self, study_key: str, form_key: str, **kwargs: Any
    ) -> List[BaseModel]:  # Changed return type annotation
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
        # Pass the correct client instances to the utility function
        return _fetch_and_parse_typed_records(
            self.variables, self.records, study_key, form_key, **kwargs
        )

    def close(self) -> None:
        """Closes the underlying HTTP client connection."""
        self._client.close()

    def __enter__(self) -> "ImednetClient":
        """Enter the runtime context related to this object."""
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Exit the runtime context related to this object."""
        self.close()
