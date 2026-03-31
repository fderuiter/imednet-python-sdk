## 2024-03-30 - Closing AsyncClient correctly within ImednetSDK context managers
**Discovery:** The `ImednetSDK.close()` function contained untested paths for handling loop retrieval. Specifically, if a `RuntimeError` was raised when `asyncio.get_running_loop()` was called, the loop was closed, or it had an active event loop that was not closed. The `test.skip` and missing tests reduced coverage of critical client clean-up paths. Additionally `test_sdk_retry_policy.py` generates `RuntimeWarning: coroutine 'AsyncMockMixin._execute_mock_call' was never awaited` when the `RetryPolicy` mock objects are evaluated via `AsyncMock()`.

**Defense:** Implement comprehensive testing for `ImednetSDK` context managers (`test_sdk_context.py`), utilizing `unittest.mock.patch` for `asyncio` to mock loop states accurately, ensuring `Client.close()` and `AsyncClient.aclose()` are reliably evaluated without generating `RuntimeWarning`s or skipping tests. The `patch` decorators and context blocks isolate `asyncio` environments correctly.

## 2025-02-15 - Unclosed Sockets Triggering ResourceWarnings as GC Artifacts
**Discovery:** Many tests initializing `ImednetSDK()` without using the context manager leaked sockets and event loops, which caused random test failures during garbage collection sweeps when running pytest with strict warnings turned on (`-W error`).
**Defense:** `ImednetSDK` connections map to lower-level `httpx.Client` resources and must ALWAYS be scoped in a `with ImednetSDK() as sdk:` block or explicitly `sdk.close()`d inside fixture teardown (`yield sdk`).
