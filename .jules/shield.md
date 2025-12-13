## 2024-05-23 - BaseEndpoint implicitly tested
**Discovery:** Protected helper methods in `BaseEndpoint` (`_fallback_from_list`, `_require_async_client`) were only tested implicitly through subclasses, leaving 22% of the base class (mostly error handling) uncovered.
**Defense:** Added `tests/unit/endpoints/test_base_endpoint.py` with a `MockEndpointImpl` to explicitly test the contract and error states of the base class.

## 2024-05-23 - Vulnerable dependencies
**Discovery:** Found CVE-2025-66471/66418 (urllib3) and CVE-2025-66221 (werkzeug) via pip-audit.
**Defense:** Updated urllib3 to ^2.6.0 and werkzeug to >=3.1.4 to patch vulnerabilities.

## 2025-12-12 - Silent Validation Skip
**Discovery:** Input validation in `RecordsEndpoint.create` was silently skipped if the user provided snake_case `form_key` (Pythonic) instead of camelCase `formKey` (API spec), leading to invalid data potentially being sent to the API.
**Defense:** Updated `create` and `async_create` to attempt resolving `formKey`, `form_key`, `formId`, and `form_id` before falling back to default, ensuring validation runs for both conventions.

## 2025-12-13 - Missing Schema Validators
**Discovery:** The `validate_record_data` function crashes with `UnknownVariableTypeError` when encountering valid API variable types (`date`, `datetime`, `time`, `radio`, `dropdown`, `checkbox`) because they were missing from the `_TYPE_VALIDATORS` map.
**Defense:** Added the missing validators to `imednet/validation/cache.py`, mapping them to string validation, and added comprehensive test coverage for these types in `test_utils_schema.py`.
