# AGENTS.md – Test Suite Rules

## Purpose
Provide ground rules for creating and maintaining **pytest** tests so that every change ships with matching, reliable coverage.

---

## Where to put new tests
- **MUST** add or update tests **in the same hierarchy** as the production file you change.
  - Example → editing `imednet/core/client.py` ⇒ place tests in `tests/core/test_client.py`.
- **DO NOT** scatter unrelated tests in arbitrary folders.

---

## Test style & tools
- Use **pytest** with strictly-typed assertions (`assert isinstance(result, MyType)`).
- Prefer **pytest-asyncio** for async code; mark async tests with `@pytest.mark.asyncio`.
- Mock HTTP traffic with **respx** or **responses** when testing offline. It's OK to hit the live iMednet API if you set `IMEDNET_RUN_E2E=1` with valid credentials and want to run the examples under `tests/live/`.
- Keep helpers that are shared across modules in `tests/conftest.py` or `tests/utils/`.

---

## Golden fixtures
- Golden JSON/CSV/etc. live under `tests/fixtures/`.
- If you modify a golden file, you **MUST** also update the corresponding assertions and add a changelog note in the test header.
- **DO NOT** delete or rewrite a golden fixture merely to silence a failing test.

---

## Coverage & performance
- Target line coverage **≥ 90 %** (`pytest --cov=imednet --cov-fail-under=90`).
- Marks:
  - Slow tests with `@pytest.mark.slow`; CI runs them on a nightly schedule.
  - Network-heavy tests with `@pytest.mark.external` and **skip** by default.

---

## Running locally  

```bash
# one-liner to run everything exactly like CI
poetry run pytest --cov=imednet --cov-fail-under=90 -q
```

All checks **MUST** pass with exit code 0 before a PR can be merged or a tag pushed.

