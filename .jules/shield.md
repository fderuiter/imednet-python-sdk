## 2024-05-23 - BaseEndpoint implicitly tested
**Discovery:** Protected helper methods in `BaseEndpoint` (`_fallback_from_list`, `_require_async_client`) were only tested implicitly through subclasses, leaving 22% of the base class (mostly error handling) uncovered.
**Defense:** Added `tests/unit/endpoints/test_base_endpoint.py` with a `MockEndpointImpl` to explicitly test the contract and error states of the base class.
