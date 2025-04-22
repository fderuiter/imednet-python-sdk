# API Alignment Checklist

This checklist outlines the steps to ensure the `imednet-python-sdk` code and tests align with the API reference documentation (primarily `docs/reference/openapi.yaml` and other files in `docs/reference/`).

## 1. General Checks

- [ ] **Base URL:** Verify the base URL (`client.base_url`) used by the client matches the server URLs specified in `openapi.yaml` (or other documentation). Check for environment-specific configurations (dev, staging, prod).
- [ ] **Authentication:**
  - [ ] Verify the authentication mechanism (e.g., API keys, OAuth tokens) implemented in `client.py` matches the security schemes defined in `openapi.yaml` or `docs/reference/2 header.md`.
  - [ ] Verify how credentials (API key, token) are obtained, stored, and included in requests (e.g., headers like `Authorization`, `X-API-Key`).
  - [ ] Verify token refresh logic (if applicable) aligns with documentation.
  - [ ] Verify handling of authentication errors (e.g., 401 Unauthorized, 403 Forbidden) matches `docs/reference/3 error.md`.
- [ ] **Error Handling (`exceptions.py`):**
  - [ ] Review general error handling mechanisms (`_handle_response` in `_base.py`).
  - [ ] Ensure SDK exceptions map correctly to documented HTTP status codes (4xx, 5xx) and error response formats (e.g., `{"error": {"code": "...", "message": "..."}}`) as defined in `openapi.yaml` or `docs/reference/3 error.md`.
  - [ ] Verify specific custom exceptions are raised for documented error conditions.
- [ ] **Versioning:**
  - [ ] Check if the API uses versioning (e.g., in the URL path or headers).
  - [ ] Ensure the SDK targets the correct API version as documented.
  - [ ] Check if the SDK's versioning strategy (`pyproject.toml`) relates to or tracks the API version.
- [ ] **Headers:**
  - [ ] Verify standard request headers (e.g., `Content-Type`, `Accept`) sent by the SDK match API expectations (often `application/json`).
  - [ ] Verify handling of standard response headers (e.g., `Content-Type`, rate limiting headers if documented).
- [ ] **Rate Limiting:** Check if the documentation mentions rate limits and if the SDK includes any mechanisms (e.g., automatic retries, backoff) to handle `429 Too Many Requests` errors.

## 2. API Endpoint Alignment (`imednet_sdk/api/`)

For each endpoint defined in `docs/reference/openapi.yaml` (or corresponding `.md` files in `docs/reference/`) and implemented in `imednet_sdk/api/`:

- Identify the relevant documentation source (`openapi.yaml` path/operation or specific `.md` file).
- Compare the implementation in the corresponding Python file (`imednet_sdk/api/*.py`).

**For each specific API (Codings, Forms, Intervals, etc.):**

- [ ] **Method Signatures:**
  - [ ] Verify Python method names clearly map to API operations.
  - [ ] Verify required and optional parameters (including types and default values) match the documentation (path parameters, query parameters, request body).
  - [ ] Verify docstrings accurately reflect the API operation and parameters based on the documentation.
- [ ] **Request Construction:**
  - [ ] Verify URL paths are constructed correctly, including path parameters.
  - [ ] Verify HTTP methods (GET, POST, PUT, DELETE, etc.) match the documentation.
  - [ ] Verify query parameters are correctly encoded and included in the URL.
  - [ ] Verify the request body (for POST, PUT) is serialized correctly according to the documented schema (`requestBody` in OpenAPI).
  - [ ] Verify correct `Content-Type` header is set for requests with bodies.
- [ ] **Response Handling:**
  - [ ] Verify expected success status codes (e.g., 200, 201, 204) are handled correctly.
  - [ ] Verify the response body is deserialized correctly based on the documented success response schema (`responses` in OpenAPI).
  - [ ] Verify documented error status codes (4xx, 5xx) are handled and raise appropriate exceptions (see General Checks > Error Handling).
  - [ ] Verify relevant response headers (e.g., `Location` for 201 Created) are processed if needed.
- [ ] **Pagination/Filtering/Sorting:**
  - [ ] If the endpoint supports pagination, verify parameters (`limit`, `offset`, `page`, cursor-based, etc.) are implemented as documented.
  - [ ] If the endpoint supports filtering or sorting, verify the corresponding query parameters are implemented correctly.

*(Repeat the above checks for each API module: `codings.py`, `forms.py`, `intervals.py`, `jobs.py`, `queries.py`, `record_revisions.py`, `records.py`, `sites.py`, `studies.py`, `subjects.py`, `users.py`, `variables.py`, `visits.py`)*

- [ ] **Common/Other Endpoints (Check `_base.py`, `client.py`):**
  - [ ] Verify any utility methods making API calls (if any) align with documentation.

## 3. Data Model Alignment (`imednet_sdk/models/`)

For each data model (schema object) defined in the API documentation (`openapi.yaml#/components/schemas` or other reference files):

- [ ] **Existence & Naming:**
  - [ ] Verify a corresponding Python model class exists in `imednet_sdk/models/`.
  - [ ] Verify the Python class name reflects the schema name.
  - [ ] Verify model field names match the documentation properties (check case: `snake_case` in Python vs. `camelCase` in JSON API is common; ensure mapping is correct).
- [ ] **Fields & Types:**
  - [ ] Verify all documented properties exist as fields/attributes in the Python model.
  - [ ] Verify Python data types (e.g., `str`, `int`, `float`, `bool`, `datetime`, `List`, `Optional`) correctly map to the documented schema types and formats (e.g., `string`, `integer`, `number`, `boolean`, `string<date-time>`).
  - [ ] Verify handling of required vs. optional fields (e.g., use of `Optional[...]` in Python) matches the `required` list in the schema.
  - [ ] Verify handling of nullable fields matches `nullable: true` in the schema.
  - [ ] Verify enum values defined in the schema are correctly represented (e.g., using Python `Enum` or `Literal`).
  - [ ] Verify constraints mentioned in documentation (e.g., min/max length, patterns) are considered (though often not strictly enforced in basic models).
- [ ] **Nested Models:** Verify fields that reference other schemas correctly use the corresponding nested Python models.
- [ ] **Serialization/Deserialization:**
  - [ ] Verify logic (e.g., if using Pydantic or custom methods) correctly converts between the JSON API format (e.g., `camelCase`) and the Python model format (e.g., `snake_case`).
  - [ ] Pay special attention to date/time formats during serialization/deserialization.

## 4. Test Alignment (`tests/`)

Goal: Ensure tests provide comprehensive validation that the SDK behaves exactly as expected according to the API documentation.

For each API endpoint, data model, and major client functionality:

- [ ] **Overall Test Structure & Coverage:**
  - [ ] Verify a logical test structure exists (e.g., `tests/api/test_<resource>.py`, `tests/models/test_<model>.py`).
  - [ ] Verify test files exist for *all* API modules in `imednet_sdk/api/`.
  - [ ] Verify test files exist for *all* data models in `imednet_sdk/models/`.
  - [ ] Verify tests cover core client logic (`tests/test_client.py`), including initialization, authentication, and base request handling.
  - [ ] Verify tests cover utility functions (`tests/test_utils.py`), especially those involved in request/response processing.
  - [ ] Consider using coverage tools (`pytest-cov`) to identify untested code paths.

- [ ] **API Tests (`tests/api/test_*.py`):** (Perform these checks for *each method* in *each* API module)
  - [ ] **Mocking Strategy:**
    - [ ] Ensure a consistent mocking strategy is used (e.g., `unittest.mock`, `pytest-mock`, `requests-mock`).
    - [ ] Ensure mocks accurately simulate API behavior, including status codes, headers, and response bodies based *strictly* on `openapi.yaml` or `.md` documentation.
  - [ ] **Success Cases (Happy Path):**
    - [ ] Test each API method with valid inputs for all required parameters.
    - [ ] Mock a successful API response (e.g., 200 OK, 201 Created, 204 No Content) with a response body matching the documented schema/example.
    - [ ] **Assert Request Details:** Verify the mock was called with:
      - [ ] The correct HTTP method (GET, POST, PUT, DELETE, etc.).
      - [ ] The correctly constructed URL (including base URL, path, and path parameters).
      - [ ] Correctly formatted query parameters (if applicable).
      - [ ] Correct request headers (e.g., `Authorization`, `Content-Type`, `Accept`).
      - [ ] Correctly serialized request body (for POST/PUT) matching the documented schema.
    - [ ] **Assert Response Handling:**
      - [ ] Verify the SDK method returns the expected Python object(s) (e.g., instances of `imednet_sdk.models.*`).
      - [ ] Verify the data within the returned object(s) accurately reflects the mocked response body, including correct types and nested structures.
      - [ ] If the API returns no content (204), verify the SDK method returns `None` or handles it appropriately.
  - [ ] **Error Cases:**
    - [ ] Test documented client errors (e.g., 400 Bad Request, 401 Unauthorized, 403 Forbidden, 404 Not Found, 422 Unprocessable Entity) by providing relevant invalid input or mocking the error response.
    - [ ] Mock the specific error response (status code, error body format) based *exactly* on `docs/reference/3 error.md` or `openapi.yaml`.
    - [ ] Assert that the correct, specific SDK exception (e.g., `BadRequestError`, `AuthenticationError`, `NotFoundError` from `imednet_sdk.exceptions`) is raised.
    - [ ] Test documented server errors (e.g., 500 Internal Server Error, 503 Service Unavailable) and assert appropriate exceptions are raised.
  - [ ] **Parameter Validation & Edge Cases:**
    - [ ] Test sending different valid combinations of *optional* parameters and verify they are included correctly in the request.
    - [ ] Test edge cases for parameter values (e.g., empty strings, zero values, empty lists, large values) where applicable based on documentation constraints.
    - [ ] Test parameter validation *within* the SDK if any exists (e.g., raising `ValueError` before making the API call).
  - [ ] **Pagination/Filtering/Sorting Tests:**
    - [ ] If the endpoint supports pagination, test that pagination parameters (`limit`, `offset`, etc.) are correctly passed in the request URL.
    - [ ] Test handling of paginated responses, especially if the SDK provides helper methods or iterators.
    - [ ] If the endpoint supports filtering/sorting, test that various filter/sort parameters are correctly formatted and included in the request URL.

- [ ] **Client Tests (`tests/test_client.py`):**
  - [ ] Test client initialization with valid API keys/tokens and base URLs.
  - [ ] Test client initialization with invalid or missing credentials/URLs, asserting appropriate errors.
  - [ ] Verify the `Authorization` or other auth headers are correctly constructed and added by the client's request methods.
  - [ ] Test any session management or token refresh logic if applicable and documented.
  - [ ] Test base URL construction for different environments if supported.
  - [ ] Test default headers (`Accept`, `Content-Type`, User-Agent) are set correctly.
  - [ ] Test timeout configurations.

- [ ] **Model Tests (`tests/models/test_*.py`):** (Perform these checks for *each* model)
  - [ ] **Instantiation:**
    - [ ] Test model instantiation with dictionary data matching documented examples/schemas (representing typical API response data).
    - [ ] Test instantiation with keyword arguments.
    - [ ] Verify all fields are correctly populated with the expected types.
    - [ ] Test handling of required, optional, and nullable fields during instantiation (e.g., assert errors for missing required fields if applicable, verify `None` is allowed for optional/nullable).
    - [ ] Test instantiation with nested models.
  - [ ] **Serialization (e.g., to dict/JSON for API requests):**
    - [ ] If models are used in request bodies, test serialization methods (e.g., a `.to_dict()` method or Pydantic's `.model_dump(mode='json')`).
    - [ ] Assert that the output dictionary/JSON has the correct field names (e.g., `camelCase` if required by the API) and structure matching the documented request schema.
    - [ ] Verify correct serialization of different data types (especially dates, enums, nested models).
    - [ ] Verify optional fields with `None` values are handled correctly (e.g., omitted or included as `null` based on API requirements).
  - [ ] **Deserialization (e.g., from API response JSON):**
    - [ ] Test model creation from dictionary data simulating an API response (e.g., using Pydantic's `model_validate` or a custom factory).
    - [ ] Assert that JSON field names (e.g., `camelCase`) correctly map to Python model attributes (e.g., `snake_case`).
    - [ ] Verify correct parsing of different data types (dates, enums, nested models).
    - [ ] Test robustness against unexpected or extra fields in the response data (should typically be ignored).

- [ ] **Mock Data Accuracy:**
  - [ ] Cross-reference all mock request/response bodies used in tests against the `openapi.yaml` schemas and examples in `.md` files.
  - [ ] Ensure mock data covers variations (e.g., optional fields present/absent, different enum values).
  - [ ] Consider storing complex mock data in separate fixture files (`tests/fixtures/`) for clarity.

- [ ] **Test Refactoring & Readability:**
  - [ ] Review existing tests for clarity, conciseness, and maintainability.
  - [ ] Consider refactoring complex tests or repetitive setup code using fixtures (`pytest` fixtures are recommended).
  - [ ] Ensure test names clearly describe the scenario being tested.
  - [ ] Ensure assertions are specific and provide informative failure messages.

## 5. Documentation Examples (`examples/`)

- [ ] Review code examples in the `examples/` directory.
- [ ] Verify that the examples accurately reflect the *current* SDK usage for the demonstrated endpoints/features.
- [ ] Verify the parameters, request patterns, and response handling shown in examples align with the API documentation (`openapi.yaml`, `.md` files).
- [ ] Ensure examples include necessary setup (client initialization, authentication).
- [ ] Ensure examples demonstrate basic error handling (e.g., try/except blocks for SDK exceptions).
- [ ] Ensure examples are functional and produce the expected output based on the documentation.
- [ ] Add examples for newly added or significantly changed features.
