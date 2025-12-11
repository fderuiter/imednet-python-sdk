## 2024-05-23 - BaseEndpoint implicitly tested
**Discovery:** Protected helper methods in `BaseEndpoint` (`_fallback_from_list`, `_require_async_client`) were only tested implicitly through subclasses, leaving 22% of the base class (mostly error handling) uncovered.
**Defense:** Added `tests/unit/endpoints/test_base_endpoint.py` with a `MockEndpointImpl` to explicitly test the contract and error states of the base class.

## 2024-05-23 - Vulnerable dependencies
**Discovery:** Found CVE-2025-66471/66418 (urllib3) and CVE-2025-66221 (werkzeug) via pip-audit.
**Defense:** Updated urllib3 to ^2.6.0 and werkzeug to >=3.1.4 to patch vulnerabilities.
