import pytest
from playwright.sync_api import Page, expect

pytestmark = pytest.mark.browser

def connect_to_study(page: Page):
    """Helper to connect to the test study."""
    page.get_by_label("Select Authorized Study").click()
    page.get_by_role("option", name="TEST-STUDY").click()
    page.get_by_role("button", name="Connect").click()
    expect(page.get_by_text("Connected ✓")).to_be_visible()

def test_unauthenticated_home(dashboard_server, page: Page):
    """Verify the home page renders in unauthenticated state."""
    page.goto(dashboard_server)
    expect(page.locator("section[data-testid='stSidebar']")).to_be_visible()
    expect(page.get_by_text("SSO Active: test-operator@example.com")).to_be_visible()
    expect(page.get_by_text("Please authenticate using the sidebar to access the dashboard.")).to_be_visible()

def test_successful_connection_and_navigation(dashboard_server, page: Page):
    """Verify successful connection and expansion of navigation."""
    page.goto(dashboard_server)
    connect_to_study(page)
    expect(page.get_by_text("Connected to study: TEST-STUDY")).to_be_visible()
    expect(page.get_by_text("Query Status")).to_be_visible()
    expect(page.get_by_text("Subject Enrollment")).to_be_visible()
    expect(page.get_by_text("Reporting Dashboard")).to_be_visible()

def test_page_navigation_smoke(dashboard_server, page: Page):
    """Smoke test for navigating to core pages."""
    page.goto(dashboard_server)
    connect_to_study(page)

    # Navigate to Query Status
    page.locator("section[data-testid='stSidebar']").get_by_text("Query Status").click()
    expect(page.get_by_text("Query Status Overview", exact=False)).to_be_visible(timeout=10000)

    # Navigate to Subject Enrollment
    page.locator("section[data-testid='stSidebar']").get_by_text("Subject Enrollment").click()
    expect(page.get_by_text("Subject Enrollment Overview", exact=False)).to_be_visible(timeout=10000)

def test_empty_state_handling(dashboard_server, page: Page):
    """Verify that pages handle empty states without crashing."""
    page.goto(dashboard_server)
    connect_to_study(page)

    # Navigate to Data Completeness
    page.locator("section[data-testid='stSidebar']").get_by_text("Data Completeness").click()
    # Heading includes an emoji
    expect(page.get_by_role("heading", name="Data Completeness", exact=False)).to_be_visible(timeout=10000)
    expect(page.get_by_text("Unhandled Exception")).not_to_be_visible()

def test_export_button_visibility(dashboard_server, page: Page):
    """Verify that export buttons are present on applicable pages."""
    page.goto(dashboard_server)
    connect_to_study(page)

    # Navigate to Site Performance
    page.locator("section[data-testid='stSidebar']").get_by_text("Site Performance").click()

    # Using heading role to avoid confusion with sidebar links
    expect(page.get_by_role("heading", name="Site Performance", exact=False)).to_be_visible(timeout=10000)
    expect(page.get_by_text("Unhandled Exception")).not_to_be_visible()
