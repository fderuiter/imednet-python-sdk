import datetime  # Added for timestamp
import os
from typing import Any, Dict, List, Optional, Set, Type, TypeVar, Union

import httpx
from pydantic import BaseModel, TypeAdapter, ValidationError
# Import tenacity for retry logic
from tenacity import (RetryError, retry, retry_if_exception, retry_if_exception_type,
                      stop_after_attempt, wait_exponential)

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
        backoff_factor: float = 1,  # Tenacity uses 'multiplier' in wait_exponential
        # retry_statuses: Optional[Set[int]] = None, # Replaced by retry_exceptions
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
        self._backoff_factor = backoff_factor  # Store for tenacity wait config
        # self._retry_statuses = ( # No longer needed
        #     retry_statuses if retry_statuses is not None else DEFAULT_RETRYABLE_STATUS_CODES
        # )
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

        # Note: httpx's built-in retries via HTTPTransport are more robust,
        # but implementing manually for now as per original structure.
        self._client = httpx.Client(
            base_url=self.base_url,
            headers=self._default_headers,
            timeout=self._default_timeout,
        )

        # Resource client initialization moved to properties

    def _make_request_attempt(
        self,
        method: str,
        url: str,  # Pass url directly now
        params: Optional[Dict[str, Any]],
        request_json: Optional[Any],  # Pass pre-processed json
        request_timeout: TimeoutTypes,  # Pass calculated timeout
        response_model: Optional[Union[Type[T], Type[List[T]]]],
        **kwargs: Any,
    ) -> Union[T, List[T], httpx.Response]:
        """Makes a single HTTP request attempt and handles response/errors."""
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
        """Internal method to make HTTP requests with error handling, tenacity retry logic, and deserialization."""
        url = endpoint
        request_timeout = timeout if timeout is not None else self._default_timeout
        # last_exception: Optional[Exception] = None # Handled by tenacity

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

        # --- Old Manual Retry Logic (Removed) ---
        # for attempt in range(self._retries + 1):
        #     request_path = str(
        #         self._client.build_request(method, url, params=params, json=request_json).url
        #     )
        #     try:
        #         response = self._client.request(
        #             method=method,
        #             url=url,
        #             params=params,
        #             json=request_json,
        #             timeout=request_timeout,
        #             **kwargs,
        #         )
        #         if not response.is_success:
        #             # Check if status code is retryable AND method allows retry
        #             if (
        #                 attempt < self._retries
        #                 and response.status_code in self._retry_statuses
        #                 and method.upper() in self._retry_methods
        #             ):
        #                 last_exception = ImednetSdkException(f"HTTP error {response.status_code} on attempt {attempt+1}", status_code=response.status_code, request_path=request_path) # Store temp exception
        #                 delay = self._calculate_backoff(attempt + 1) # Use attempt+1 for backoff calc
        #                 time.sleep(delay)
        #                 continue # Retry

        #             # If not retryable, handle the API error (which raises)
        #             self._handle_api_error(response, request_path)

        #         # --- Success Path ---
        #         if response_model is None:
        #             return response
        #         try:
        #             response_data = response.json()
        #         except ValueError as json_exc:
        #             raise RuntimeError(f"Failed to decode JSON response: {json_exc}") from json_exc
        #         try:
        #             adapter = TypeAdapter(response_model)
        #             validated_data = adapter.validate_python(response_data)
        #             return validated_data
        #         except ValidationError as validation_exc:
        #             raise RuntimeError(
        #                 f"Failed to validate response data: {validation_exc}"
        #             ) from validation_exc

        #     except httpx.RequestError as exc:
        #         last_exception = exc
        #         if (
        #             attempt < self._retries
        #             and type(exc) in self._retry_exceptions
        #             and method.upper() in self._retry_methods
        #         ):
        #             delay = self._calculate_backoff(attempt + 1) # Use attempt+1 for backoff calc
        #             time.sleep(delay)
        #             continue # Retry
        #         else:
        #             raise # Non-retryable or max retries reached

        # # Raise the last recorded exception if all retries failed
        # if last_exception:
        #     # If the last exception was our temporary one for retryable status codes,
        #     # call _handle_api_error again to get the *correct* custom exception type.
        #     # This requires storing the last response, which adds complexity.
        #     # For now, just raise the last exception captured.
        #     # A better approach is needed here if we want the specific custom exception after status retries fail.
        #     # *** Tenacity handles this better by re-raising the actual exception ***
        #     raise last_exception
        # else:
        #     raise RuntimeError("Request failed without capturing an exception after retries.")

    def _handle_api_error(self, response: httpx.Response, request_path: str) -> None:
        """Parses API error responses and raises the appropriate custom exception."""
        # Ensure this method raises the correct exception based on status/code
        # The exceptions raised here (RateLimitError, ApiError) will be caught
        # by tenacity if they are in self._retry_exceptions_tuple
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
            # This exception might trigger a retry if method is GET and RateLimitError is in retry_exceptions
            raise RateLimitError(**exception_args)
        elif status_code >= 500:  # Catches 500, 503 etc.
            # This exception might trigger a retry if method is GET and ApiError is in retry_exceptions
            raise ApiError(**exception_args)
        elif status_code >= 400:  # Other 4xx errors (e.g., 405)
            # Typically not retried, raise ApiError or BadRequestError? Using ApiError for now.
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
