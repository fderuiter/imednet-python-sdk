import datetime  # Added for timestamp
import os
import random
import time
from typing import Any, Dict, List, Optional, Set, Type, TypeVar, Union

import httpx
from pydantic import BaseModel, TypeAdapter, ValidationError

# Import resource clients
from .api import (CodingsClient, FormsClient, IntervalsClient, JobsClient, RecordRevisionsClient,
                  RecordsClient, SitesClient, StudiesClient, SubjectsClient, UsersClient,
                  VariablesClient, VisitsClient)
# Import custom exceptions
from .exceptions import (ApiError, AuthenticationError, AuthorizationError, BadRequestError,
                         ImednetSdkException, NotFoundError, RateLimitError)
from .exceptions import ValidationError as SdkValidationError  # Alias to avoid name clash

# Define a TypeVar for generic response models
T = TypeVar("T", bound=BaseModel)

# Type alias for timeout configuration
TimeoutTypes = Union[float, httpx.Timeout, None]

# Define retryable exceptions and status codes - Will be revisited for tenacity integration
DEFAULT_RETRYABLE_STATUS_CODES: Set[int] = {500, 502, 503, 504}
DEFAULT_RETRYABLE_METHODS: Set[str] = {
    "GET",
    "POST",
}  # Assuming POST is idempotent or safe to retry for this API
DEFAULT_RETRYABLE_EXCEPTIONS: Set[type] = {httpx.ConnectError, httpx.ReadTimeout, httpx.PoolTimeout}


class ImednetClient:
    """Core HTTP client for interacting with the iMednet API."""

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
        backoff_factor: float = 0.5,  # Default backoff factor (e.g., 0.5, 1, 1.5, ... seconds)
        retry_statuses: Optional[Set[int]] = None,
        retry_methods: Optional[Set[str]] = None,
        retry_exceptions: Optional[Set[type]] = None,
    ):
        """Initializes the ImednetClient.

        Args:
            api_key: Your iMednet API key. If None, reads from IMEDNET_API_KEY env var.
            security_key: Your iMednet Security key. If None, reads from IMEDNET_SECURITY_KEY
                env var.
            base_url: The base URL for the iMednet API. Defaults to production.
            timeout: Default request timeout configuration.
            retries: Number of retry attempts for transient errors.
            backoff_factor: Factor to determine delay between retries
                            (delay = backoff_factor * (2 ** attempt)).
            retry_statuses: Set of HTTP status codes to retry on.
                            Defaults to {500, 502, 503, 504}.
            retry_methods: Set of HTTP methods to allow retries for.
                           Defaults to {"GET", "POST"}.
            retry_exceptions: Set of httpx exception types to retry on.
                              Defaults to {ConnectError, ReadTimeout,
                              PoolTimeout}.

        Raises:
            ValueError: If api_key or security_key is not provided and cannot be found
                        in environment variables (placeholder for AuthenticationError).
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
        self._backoff_factor = backoff_factor
        self._retry_statuses = (
            retry_statuses if retry_statuses is not None else DEFAULT_RETRYABLE_STATUS_CODES
        )
        self._retry_methods = (
            retry_methods if retry_methods is not None else DEFAULT_RETRYABLE_METHODS
        )
        self._retry_exceptions = (
            retry_exceptions if retry_exceptions is not None else DEFAULT_RETRYABLE_EXCEPTIONS
        )

        self._default_headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "x-api-key": self._api_key,
            "x-imn-security-key": self._security_key,
        }

        # Note: httpx's built-in retries via HTTPTransport are more robust,
        # but implementing manually for now as per original structure.
        self._client = httpx.Client(
            base_url=self.base_url,
            headers=self._default_headers,
            timeout=self._default_timeout,
        )

        # Resource client initialization moved to properties

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
        """Internal method to make HTTP requests with error handling, retry logic, and deserialization."""
        url = endpoint
        request_timeout = timeout if timeout is not None else self._default_timeout
        last_exception: Optional[Exception] = None

        # Handle potential Pydantic model serialization for request body
        request_json = None
        if isinstance(json, BaseModel):
            # Serialize Pydantic model to dict using aliases
            request_json = json.model_dump(by_alias=True, mode="json")
        elif json is not None:
            request_json = json  # Assume it's already a dict/serializable

        for attempt in range(self._retries + 1):
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
                # Check for non-2xx responses BEFORE raise_for_status to handle custom exceptions
                if not response.is_success:
                    self._handle_api_error(response, request_path)  # Raise custom exception here

                # Raise HTTPStatusError for non-2xx responses if not handled above (shouldn't happen now)
                # response.raise_for_status() # Removed, handled by _handle_api_error

                # If no response model is specified, return the raw response
                if response_model is None:
                    return response

                # Step 1: Try to decode JSON
                try:
                    response_data = response.json()
                except ValueError as json_exc:  # Catches JSONDecodeError
                    # Handle cases where response is not valid JSON
                    raise RuntimeError(f"Failed to decode JSON response: {json_exc}") from json_exc

                # Step 2: Try to validate the decoded JSON data
                try:
                    adapter = TypeAdapter(response_model)
                    validated_data = adapter.validate_python(response_data)
                    return validated_data
                except ValidationError as validation_exc:
                    # Handle Pydantic validation errors
                    raise RuntimeError(
                        f"Failed to validate response data: {validation_exc}"
                    ) from validation_exc

            # except httpx.HTTPStatusError as exc: # Replaced by direct status check and _handle_api_error
            #     # This block is now handled by the check `if not response.is_success:` and `_handle_api_error`
            #     pass

            except httpx.RequestError as exc:  # Keep retry for connection errors etc.
                last_exception = exc
                # Check if we should retry based on exception type and method
                if (
                    attempt < self._retries
                    and type(exc) in self._retry_exceptions
                    and method.upper() in self._retry_methods
                ):
                    delay = self._calculate_backoff(attempt)
                    time.sleep(delay)
                    continue  # Retry
                else:
                    # Wrap non-HTTP errors in our base exception for consistency? Or re-raise? Re-raise for now.
                    # raise ImednetSdkException(f"Request failed due to network/transport error: {exc}", request_path=request_path) from exc
                    raise  # Non-retryable exception/method or max retries reached

        # Should be unreachable if retries >= 0, but satisfy type checker
        # and handle edge case of retries < 0
        if last_exception:
            raise last_exception
        else:
            # This case should ideally never happen in normal flow
            raise RuntimeError("Request failed without capturing an exception after retries.")

    def _handle_api_error(self, response: httpx.Response, request_path: str) -> None:
        """Parses API error responses and raises the appropriate custom exception."""
        status_code = response.status_code
        timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
        error_details: Dict[str, Any] = {}
        api_error_code: Optional[str] = None
        description: str = f"HTTP error {status_code} occurred."
        attribute: Optional[str] = None
        value: Optional[Any] = None

        try:
            error_data = response.json()
            # Safely access nested dictionary keys
            metadata = error_data.get("metadata", {})
            error_info = metadata.get("error", {})

            api_error_code = error_info.get("code")
            description = error_info.get(
                "description", description
            )  # Use parsed description if available
            attribute = error_info.get("attribute")
            value = error_info.get("value")
            error_details = error_data  # Store the full parsed body

        except ValueError:  # Includes JSONDecodeError
            description = (
                f"HTTP error {status_code} occurred, and the response body was not valid JSON."
            )
            error_details = {"raw_response": response.text}  # Store raw text if not JSON

        # Exception Mapping Logic
        exception_args = {
            "message": description,
            "status_code": status_code,
            "api_error_code": api_error_code,
            "request_path": request_path,
            "response_body": error_details,
            "timestamp": timestamp,
        }

        if status_code == 400:
            if api_error_code == "1000":  # Validation Error
                raise SdkValidationError(**exception_args, attribute=attribute, value=value)
            else:  # General Bad Request
                raise BadRequestError(**exception_args)
        elif status_code == 401:
            # API docs mention code 9001 specifically for invalid keys
            # message = "Authentication failed: Invalid API key or Security key." if api_error_code == "9001" else description
            # exception_args["message"] = message # Update message for specific code
            raise AuthenticationError(**exception_args)
        elif status_code == 403:
            raise AuthorizationError(**exception_args)
        elif status_code == 404:
            raise NotFoundError(**exception_args)
        elif status_code == 429:
            raise RateLimitError(**exception_args)
        elif status_code == 500:
            # API docs mention code 9000 specifically for unknown server error
            # message = "An unknown internal server error occurred." if api_error_code == "9000" else description
            # exception_args["message"] = message # Update message for specific code
            raise ApiError(**exception_args)
        elif status_code >= 500:  # Other 5xx errors
            raise ApiError(**exception_args)
        elif status_code >= 400:  # Other 4xx errors
            # Default to BadRequest for other 4xx? Or a more generic ClientError? Use ApiError for now.
            raise ApiError(
                **exception_args
            )  # Or maybe BadRequestError? Let's use ApiError as a catch-all for unexpected client/server errors.
        else:
            # This should not be reached if called correctly, but handle defensively
            raise ImednetSdkException(
                f"Unhandled HTTP status code {status_code}.",
                status_code=status_code,
                request_path=request_path,
                response_body=error_details,
                timestamp=timestamp,
            )

    def _calculate_backoff(self, attempt: int) -> float:
        """Calculates exponential backoff delay with jitter."""
        if attempt == 0:
            return 0  # No delay for the first retry
        base_delay = self._backoff_factor * (2 ** (attempt - 1))
        # Add jitter: delay +/- 50% of base delay
        jitter = random.uniform(-0.5, 0.5) * base_delay
        return max(0, base_delay + jitter)

    def _get(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        response_model: Optional[Union[Type[T], Type[List[T]]]] = None,
        timeout: TimeoutTypes = None,
        **kwargs: Any,
    ) -> Union[T, List[T], httpx.Response]:
        """Sends a GET request and deserializes the response if response_model is provided."""
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
        """Sends a POST request and deserializes the response if response_model is provided."""
        return self._request(
            "POST", endpoint, json=json, response_model=response_model, timeout=timeout, **kwargs
        )

    # --- Resource Client Properties ---

    @property
    def studies(self) -> StudiesClient:
        """Access the Studies API client."""
        if self._studies is None:
            self._studies = StudiesClient(self)
        return self._studies

    @property
    def sites(self) -> SitesClient:
        """Access the Sites API client."""
        if self._sites is None:
            self._sites = SitesClient(self)
        return self._sites

    @property
    def forms(self) -> FormsClient:
        """Access the Forms API client."""
        if self._forms is None:
            self._forms = FormsClient(self)
        return self._forms

    @property
    def intervals(self) -> IntervalsClient:
        """Access the Intervals API client."""
        if self._intervals is None:
            self._intervals = IntervalsClient(self)
        return self._intervals

    @property
    def records(self) -> RecordsClient:
        """Access the Records API client."""
        if self._records is None:
            self._records = RecordsClient(self)
        return self._records

    @property
    def record_revisions(self) -> RecordRevisionsClient:
        """Access the Record Revisions API client."""
        if self._record_revisions is None:
            self._record_revisions = RecordRevisionsClient(self)
        return self._record_revisions

    @property
    def variables(self) -> VariablesClient:
        """Access the Variables API client."""
        if self._variables is None:
            self._variables = VariablesClient(self)
        return self._variables

    @property
    def codings(self) -> CodingsClient:
        """Access the Codings API client."""
        if self._codings is None:
            self._codings = CodingsClient(self)
        return self._codings

    @property
    def subjects(self) -> SubjectsClient:
        """Access the Subjects API client."""
        if self._subjects is None:
            self._subjects = SubjectsClient(self)
        return self._subjects

    @property
    def users(self) -> UsersClient:
        """Access the Users API client."""
        if self._users is None:
            self._users = UsersClient(self)
        return self._users

    @property
    def visits(self) -> VisitsClient:
        """Access the Visits API client."""
        if self._visits is None:
            self._visits = VisitsClient(self)
        return self._visits

    @property
    def jobs(self) -> JobsClient:
        """Access the Jobs API client."""
        if self._jobs is None:
            self._jobs = JobsClient(self)
        return self._jobs

    # --- End Resource Client Properties ---

    def close(self):
        """Closes the underlying HTTP client."""
        self._client.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
