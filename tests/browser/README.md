# Streamlit Dashboard Browser E2E Tests

This directory contains end-to-end browser tests for the `imednet-streamlit` dashboard.
These tests use [Playwright](https://playwright.dev/python/) to drive a real browser session.

## Prerequisites

The tests require the following dependencies:
- `playwright`
- `pytest-playwright`
- `streamlit`
- `httpx`
- `pandas`
- `altair`
- `python-json-logger`
- `python-dotenv`
- `filelock`

You also need to install the browser binaries:
```bash
playwright install chromium
```

## Running the tests

To run the browser tests locally:

```bash
PYTHONPATH=packages/core/src:packages/plugins-workflows/src:packages/plugins-streamlit/src \
pytest tests/browser/
```

The tests will:
1. Start a local Streamlit server in the background on port 8502.
2. Initialize a Playwright browser.
3. Execute the test scenarios in `test_dashboard_e2e.py`.
4. Clean up the server and browser after completion.

## Test Scenarios

- `test_unauthenticated_home`: Verifies the initial state and OIDC/SSO prompt.
- `test_successful_connection_and_navigation`: Verifies that connecting to a study expands the sidebar navigation.
- `test_page_navigation_smoke`: Verifies that clicking sidebar links successfully loads the corresponding pages.
- `test_empty_state_handling`: Verifies that pages render correctly even with no data (mocks the SDK).
- `test_export_button_visibility`: Smoke tests pages that should have export capabilities.

## Architecture

- `conftest.py`: Contains fixtures for the dashboard server and Playwright browser. It uses `IMEDNET_BROWSER_TEST=1` to enable a test mode in the app.
- `test_enterprise.sqlite3`: A temporary database used to mock tenant credentials for the dashboard.
- `imednet_streamlit/auth.py`: Adjusted to support a "test mode" bypass for SSO and SDK mocking when `IMEDNET_BROWSER_TEST=1` is set.
