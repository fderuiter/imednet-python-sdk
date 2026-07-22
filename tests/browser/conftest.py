"""Fixtures for browser-based E2E tests."""

import os
import socket
import subprocess
import time

import pytest
from playwright.sync_api import sync_playwright


def wait_for_port(port, host='localhost', timeout=10.0):
    """Wait until a port starts accepting TCP connections."""
    start_time = time.time()
    while True:
        try:
            with socket.create_connection((host, port), timeout=1.0):
                return True
        except (OSError, ConnectionRefusedError):
            time.sleep(0.5)
            if time.time() - start_time > timeout:
                return False


@pytest.fixture(scope="package")
def dashboard_server():
    """Start the Streamlit dashboard as a background process."""
    port = 8502  # Use a different port than default
    app_path = os.path.abspath("packages/plugins-streamlit/src/imednet_streamlit/app.py")

    # Set environment variables for the test environment
    env = os.environ.copy()
    env["PYTHONPATH"] = (
        os.path.abspath("packages/core/src")
        + os.pathsep
        + os.path.abspath("packages/plugins-workflows/src")
        + os.pathsep
        + os.path.abspath("packages/plugins-streamlit/src")
    )
    env["IMEDNET_BROWSER_TEST"] = "1"

    # Temporary DB for tenant credentials
    db_path = os.path.abspath("tests/browser/test_enterprise.sqlite3")
    env["IMEDNET_TENANT_DB_PATH"] = db_path

    cmd = [
        "streamlit",
        "run",
        app_path,
        "--server.port",
        str(port),
        "--server.headless",
        "true",
        "--browser.gatherUsageStats",
        "false",
    ]

    proc = subprocess.Popen(cmd, env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    if not wait_for_port(port):
        proc.kill()
        proc.wait()

        # Run synchronously to capture and report the startup error
        try:
            result = subprocess.run(cmd, env=env, capture_output=True, timeout=5)
            stdout_data, stderr_data = result.stdout.decode(), result.stderr.decode()
        except subprocess.TimeoutExpired as e:
            stdout_data, stderr_data = (
                (e.stdout.decode() if e.stdout else ""),
                (e.stderr.decode() if e.stderr else ""),
            )

        raise RuntimeError(
            f"Streamlit failed to start on port {port}. stdout: {stdout_data}, stderr: {stderr_data}"
        )

    yield f"http://localhost:{port}"

    proc.terminate()
    try:
        proc.wait(timeout=5)
    except subprocess.TimeoutExpired:
        proc.kill()
        proc.wait()


@pytest.fixture(scope="package")
def browser():
    """Initialize Playwright and launch a browser."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        yield browser
        browser.close()


@pytest.fixture
def page(browser):
    """Create a new page for each test."""
    context = browser.new_context()
    page = context.new_page()
    yield page
    context.close()


from .visual import generate_diff


@pytest.fixture
def assert_visual_diff(request):
    """
    Fixture to assert a visual difference between a Playwright page/locator
    and a baseline image.
    """

    def _assert_diff(page_or_locator, snapshot_name, tolerance=0):
        update_baselines = request.config.getoption("--update-visual-baselines")

        baseline_dir = os.path.join(os.path.dirname(__file__), "baselines")
        os.makedirs(baseline_dir, exist_ok=True)
        baseline_path = os.path.join(baseline_dir, f"{snapshot_name}.png")

        diff_dir = os.path.join(request.config.rootpath, "reports", "visual_diffs")
        os.makedirs(diff_dir, exist_ok=True)
        diff_path = os.path.join(diff_dir, f"{snapshot_name}_diff.png")

        # Capture screenshot
        actual_bytes = page_or_locator.screenshot(animations="disabled")

        if update_baselines:
            with open(baseline_path, "wb") as f:
                f.write(actual_bytes)
            return

        match, err_msg = generate_diff(baseline_path, actual_bytes, diff_path, tolerance)
        if not match:
            pytest.fail(f"Visual diff failed for {snapshot_name}: {err_msg}")

    return _assert_diff
