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
    """Core HTTP client for interacting with the iMednet API.

    Provides methods for making authenticated requests to various API endpoints,
    handling responses, errors, and retries. It also serves as an entry point
    to access specific resource clients (e.g., studies, sites, records).

    This client is designed to be used as a context manager (using `with`).
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
        """Initializes the ImednetClient with authentication and configuration.

        Sets up the underlying HTTP client, authentication headers, and retry logic
        based on the provided parameters or environment variables.

        Args:
            api_key: Your iMednet API key. If None, reads from the
                `IMEDNET_API_KEY` environment variable.
            security_key: Your iMednet Security key. If None, reads from the
                `IMEDNET_SECURITY_KEY` environment variable.
            base_url: The base URL for the iMednet API. Defaults to the production
                URL (`https://edc.prod.imednetapi.com`).
            timeout: Default request timeout configuration. Can be a float (total
                timeout) or an `httpx.Timeout` object. Defaults to 30s total, 5s connect.
            retries: Number of retry attempts for failed requests eligible for retry.
                Defaults to 3.
            backoff_factor: Multiplier for exponential backoff between retries, used by
                `tenacity.wait_exponential`. Delay = `backoff_factor * (2 ** (attempt - 1))`.
                Defaults to 1.
            retry_methods: Set of HTTP methods (uppercase) to allow retries for.
                           Defaults to `{"GET"}`.
            retry_exceptions: Set of exception types that trigger a retry attempt.
                              Defaults include various `httpx` network errors,
                              `RateLimitError` (429), and `ApiError` (5xx). User-provided
                              exceptions are added to this default set.

        Raises:
            ValueError: If `api_key` or `security_key` is not provided directly
                        and cannot be found in the corresponding environment variables
                        (`IMEDNET_API_KEY`, `IMEDNET_SECURITY_KEY`).
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
        """Makes a single HTTP request, handles API errors by raising exceptions,
        and deserializes the response if a model is provided.

        Network-related errors (`httpx.RequestError`) are allowed to propagate
        to be potentially handled by the retry logic in `_request`.
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

    def get_typed_records(
        self, study_key: str, form_key: str, **kwargs
    ) -> List[BaseModel]:  # Type hint requires List and BaseModel
        """
        Fetches records for a specific form and parses their recordData into
        dynamically typed Pydantic objects based on the form's variable definitions.

        Args:
            study_key: The key identifying the study.
            form_key: The key identifying the form.
            **kwargs: Additional parameters passed to the underlying `list_records` call
                      (e.g., filter, sort, size, record_data_filter).

        Returns:
            A list of dynamically created Pydantic model instances, each representing
            the validated `recordData` of a fetched record for the specified form.
            Returns an empty list if no variables are found for the form or if
            no records are found.

        Raises:
            ImednetSdkException: If fetching variables or records fails.
            ValueError: If building the dynamic model fails (e.g., missing variableName).
        """
        # Delegate the implementation to the helper function in utils.py
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
        """Closes the underlying HTTP client connection pool."""
        self._client.close()

    def __enter__(self):
        """Enter the runtime context related to this object."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit the runtime context and close the client connection pool."""
        self.close()
