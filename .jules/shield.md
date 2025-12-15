## 2024-05-23 - BaseEndpoint implicitly tested
**Discovery:** Protected helper methods in `BaseEndpoint` (`_fallback_from_list`, `_require_async_client`) were only tested implicitly through subclasses, leaving 22% of the base class (mostly error handling) uncovered.
**Defense:** Added `tests/unit/endpoints/test_base_endpoint.py` with a `MockEndpointImpl` to explicitly test the contract and error states of the base class.

## 2024-05-23 - Vulnerable dependencies
**Discovery:** Found CVE-2025-66471/66418 (urllib3) and CVE-2025-66221 (werkzeug) via pip-audit.
**Defense:** Updated urllib3 to ^2.6.0 and werkzeug to >=3.1.4 to patch vulnerabilities.

## 2025-12-12 - Silent Validation Skip
**Discovery:** Input validation in `RecordsEndpoint.create` was silently skipped if the user provided snake_case `form_key` (Pythonic) instead of camelCase `formKey` (API spec), leading to invalid data potentially being sent to the API.
**Defense:** Updated `create` and `async_create` to attempt resolving `formKey`, `form_key`, `formId`, and `form_id` before falling back to default, ensuring validation runs for both conventions.

## 2025-05-24 - Environment Variable Leakage
**Discovery:** Tests for configuration arguments were passing implicitly because they fell back to the environment variables present in the test runner, masking potential defects in argument handling.
**Defense:** Explicitly use `monkeypatch.delenv()` to clear environment variables in tests that verify argument prioritization or default behavior, ensuring strict isolation.
