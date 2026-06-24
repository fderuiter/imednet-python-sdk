"""Fixtures for browser-based E2E tests."""

import os
import socket
import subprocess
import time

import pytest
from playwright.sync_api import sync_playwright


def wait_for_port(port, host="localhost", timeout=10.0):
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


@pytest.fixture(scope="session")
def dashboard_server():
    """Start the Streamlit dashboard as a background process."""
    port = 8502  # Use a different port than default
    app_path = os.path.abspath(
        "packages/plugins-streamlit/src/imednet_streamlit/app.py"
    )

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

    proc = subprocess.Popen(
        cmd, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )

    if not wait_for_port(port):
        stdout, stderr = proc.communicate(timeout=1)
        proc.kill()
        raise RuntimeError(
            f"Streamlit failed to start on port {port}. stdout: {stdout.decode()}, stderr: {stderr.decode()}"
        )

    yield f"http://localhost:{port}"

    proc.terminate()
    try:
        proc.wait(timeout=5)
    except subprocess.TimeoutExpired:
        proc.kill()


@pytest.fixture(scope="session")
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
