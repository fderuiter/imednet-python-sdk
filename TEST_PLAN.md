# Test Plan for 90% Coverage - imednet-python-sdk

**Current Coverage:** (Estimate based on single smoke test - likely < 5%)
**Target Coverage:** 90%

## Overview

The current test suite only includes a basic smoke test (`tests/unit/test_smoke.py`) which checks if the main SDK class can be imported. To reach 90% coverage, we need to add unit and integration tests for core functionality, endpoints, models, utilities, and workflows.

## Areas Requiring Tests

**1. Core Components (`imednet/core`)**

* **`client.py` (ImednetClient):**
  * Test successful initialization with API keys/base URL.
  * Test handling of missing/invalid credentials.
  * Mock `httpx.Client` and test `_request` method:
    * Successful GET, POST, PUT, DELETE requests.
    * Correct header construction (API keys, Content-Type).
    * Correct URL building (base URL + path).
    * Handling of different HTTP status codes (2xx, 4xx, 5xx).
    * Parsing of successful JSON responses.
    * Raising `ApiError` on 4xx/5xx errors with correct details.
    * Retry logic (`tenacity` integration).
  * Test `get`, `post`, `put`, `delete` convenience methods.
* **`context.py` (ImednetContext):**
  * Test initialization and property access.
* **`exceptions.py`:**
  * Test initialization of `ImednetError` and `ApiError`.
  * Test string representation (`__str__`) of errors.
* **`paginator.py` (Paginator):**
  * Mock `ImednetClient.get`.
  * Test iteration over multiple pages.
  * Test handling of empty responses.
  * Test handling of responses with fewer items than `page_size`.
  * Test correct parameter construction (`page`, `size`, custom params).
  * Test handling of different `data_key` and `metadata_key` (though defaults seem standard).
  * Test error handling if the underlying client call fails.

**2. Endpoints (`imednet/endpoints`)**

* **`base.py` (BaseEndpoint):**
  * Test `_build_path` logic.
  * Test `_auto_filter` logic (if applicable beyond simple pass-through).
* **Specific Endpoints (e.g., `studies.py`, `records.py`, `subjects.py`, etc.):**
  * For *each* endpoint class:
    * Mock the `ImednetClient` passed during initialization.
    * For *each* method (e.g., `list`, `get`, `create`, `update`):
      * Test successful calls:
        * Verify the correct client method (`get`, `post`, etc.) is called.
        * Verify the correct path is constructed.
        * Verify correct parameters/payload are sent (including filters).
        * Verify the response JSON is correctly parsed into the expected Pydantic model(s) (e.g., `List[Study]`, `Record`, `Job`).
      * Test filter building (`build_filter_string` usage).
      * Test pagination usage (where applicable, e.g., `list` methods using `Paginator`).
      * Test handling of API errors raised by the client.

**3. Models (`imednet/models`)**

* For *each* Pydantic model file (e.g., `studies.py`, `records.py`, etc.):
  * For *each* model (e.g., `Study`, `Record`, `Keyword`, `QueryComment`):
    * Test successful instantiation from a dictionary (simulating API JSON).
    * Test handling of missing optional fields (should default correctly).
    * Test handling of fields with aliases (`populate_by_name=True`).
    * Test custom validators (`@field_validator`):
      * Valid input data (dates, ints, bools, strings).
      * Invalid/malformed input data (should raise `ValidationError` or handle gracefully via defaults).
      * Edge cases (e.g., empty strings, `None` values passed to validators).
    * Test `from_json` class methods if they contain logic beyond `model_validate`.
    * Test `model_dump(by_alias=True)` produces the expected dictionary structure for API calls.

**4. Utilities (`imednet/utils`)**

* **`dates.py`:**
  * Test `parse_iso_datetime` with valid and invalid ISO strings.
  * Test `format_iso_datetime` with `datetime` objects.
* **`filters.py`:**
  * Test `build_filter_string` with various dictionary inputs:
    * Simple key-value pairs.
    * Multiple key-value pairs.
    * Keys requiring special handling (e.g., date ranges - if supported).
    * Empty dictionary.
    * Dictionary with `None` values.
* **`typing.py`:** (No runtime logic to test, only type definitions).

**5. Workflows (`imednet/workflows`)**

* For *each* workflow file (e.g., `data_extraction.py`, `record_mapper.py`, etc.):
  * Mock the `ImednetSDK` instance and its endpoint methods.
  * For *each* workflow class/function:
    * Test the main execution path with mocked successful API responses.
    * Verify the correct sequence of SDK endpoint calls.
    * Verify correct parameters are passed to SDK methods.
    * Verify data aggregation/transformation logic (e.g., combining results from multiple calls, mapping data).
    * Test handling of empty or partial results from API calls.
    * Test error handling if underlying SDK calls fail.
    * **`record_mapper.py` Specific:**
      * Test DataFrame creation logic.
      * Test column naming (labels vs. names).
      * Test handling of missing variables/columns.
      * Test type conversion/validation within the DataFrame.
      * Test filtering logic (e.g., `visit_key`).
    * **`study_structure.py` Specific:**
      * Test aggregation of intervals, forms, and variables into the nested `StudyStructure` model.

**6. SDK Entrypoint (`imednet/sdk.py`)**

* Test `ImednetSDK` initialization:
  * Correct instantiation of `ImednetClient`.
  * Correct instantiation and attachment of all endpoint classes.
  * Correct instantiation and attachment of workflow classes.
  * Passing credentials and base URL correctly.

**7. CLI (`imednet/cli.py`)**

* Use `typer.testing.CliRunner`.
* Mock `get_sdk()` and the underlying SDK methods.
* For *each* command:
  * Test successful execution with required arguments/options.
  * Verify correct SDK methods are called with parsed arguments/filters.
  * Test output formatting (mock `rich.print`).
  * Test handling of missing arguments/options.
  * Test error handling (mocking `ApiError` and other exceptions).
  * Test filter argument parsing (`parse_filter_args`).

## Implementation Strategy

1. **Prioritize Core & Models:** Start with `imednet/core` and `imednet/models` as these are foundational. Ensure robust model validation and client request/error handling.
2. **Endpoints:** Test each endpoint methodically, mocking client responses.
3. **Utilities:** Cover utility functions like filter building.
4. **Workflows:** Test workflows by mocking the SDK methods they rely on.
5. **SDK & CLI:** Test the main SDK class and the CLI commands last, mocking lower-level components.
6. **Use `pytest` fixtures:** Create fixtures for initializing mocked SDKs, clients, and sample API response data.
7. **Use `responses` library:** Useful for mocking HTTP requests/responses at the `httpx` level for client tests.

By systematically adding tests for these areas, focusing on both successful paths and error conditions, the project should be able to achieve the 90% coverage target.
