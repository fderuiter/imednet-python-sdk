import pytest
from playwright.sync_api import Page, expect

pytestmark = pytest.mark.browser


def connect_to_study(page: Page):
    """Helper to connect to the test study."""
    page.get_by_label("Select Authorized Study").click()
    page.get_by_role("option", name="TEST-STUDY").click()
    page.get_by_role("button", name="Connect").click()
    expect(page.get_by_text("Connected ✓")).to_be_visible()


def test_visual_unauthenticated_home(dashboard_server, page: Page, assert_visual_diff):
    """Verify the visual layout of the home page in unauthenticated state."""
    page.goto(dashboard_server)
    expect(page.locator("section[data-testid='stSidebar']")).to_be_visible()
    expect(
        page.get_by_text("Please authenticate using the sidebar to access the dashboard.")
    ).to_be_visible()

    # Wait for things to settle
    page.wait_for_timeout(1000)

    # Capture visual diff
    assert_visual_diff(page, "unauthenticated_home", tolerance=100)


def test_visual_query_status(dashboard_server, page: Page, assert_visual_diff):
    """Verify the visual layout of the Query Status page."""
    page.goto(dashboard_server)
    connect_to_study(page)

    # Navigate to Query Status
    page.locator("section[data-testid='stSidebar']").get_by_text("Query Status").click()
    expect(page.get_by_text("Query Status Overview", exact=False)).to_be_visible(timeout=10000)

    # Wait for any data / charts to render
    page.wait_for_timeout(2000)

    # Mock some data or just screenshot what's there
    # It runs against mock datasets and fake auth contexts according to Constraints.
    assert_visual_diff(page, "query_status_overview", tolerance=100)
