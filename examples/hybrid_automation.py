import time
from typing import Any, Dict

from playwright.sync_api import sync_playwright

from imednet.form_designer.client import FormDesignerClient
from imednet.form_designer.models import Col, Entity, Layout, Page, Row, TableProps, TextFieldProps


def inject_form_specification(page, spec_data: Dict[str, Any]):
    """
    This function runs once the human has navigated to the designer.
    It scrapes the necessary tokens and uses the API to update the form.
    """
    print(">>> 🤖 AUTOMATION ENGAGED")

    # 1. Scrape the "Hidden" Context from the Page
    # We need:
    # - CSRF Key
    # - Form ID
    # - Community ID (Study ID)
    # - Revision ID (Next Revision)
    # - PHPSESSID (Cookie)

    # Note: The exact selectors here are hypothetical and based on typical legacy app patterns.
    # Users may need to adjust selectors based on the actual DOM of iMednet Form Designer.
    app_context = page.evaluate(
        """() => {
        // Helper to find value by name or id
        const getValue = (selector) => document.querySelector(selector)?.value;

        // Form ID is often in the URL or a hidden field
        const urlParams = new URLSearchParams(window.location.search);

        // Revision might be in a hidden field like 'revision' or 'next_revision'
        // or embedded in a JS object.
        // Assuming there is a global JS object or hidden fields.

        return {
            csrf_token: getValue('input[name="CSRFKey"]') || getValue('#CSRFKey'),
            form_id: urlParams.get('formId') || getValue('input[name="form_id"]'),
            community_id: getValue('input[name="community_id"]'),
            revision: getValue('input[name="revision"]'),
            base_url: window.location.origin,
            cookies: document.cookie
        }
    }"""
    )

    # Extract PHPSESSID from cookies
    cookies = app_context["cookies"]
    phpsessid = None
    if cookies:
        for cookie in cookies.split(";"):
            name, _, value = cookie.strip().partition("=")
            if name == "PHPSESSID":
                phpsessid = value
                break

    if not phpsessid:
        print(">>> ❌ Error: Could not find PHPSESSID in cookies. Are you logged in?")
        return

    # Verify we have all required fields
    required_fields = ["csrf_token", "form_id", "community_id", "revision"]
    missing_fields = [f for f in required_fields if not app_context.get(f)]

    if missing_fields:
        print(f">>> ❌ Error: Could not scrape the following fields: {', '.join(missing_fields)}")
        print(">>> Please ensure you are on the Form Designer page.")
        return

    print(
        f">>> Captured Context: FormID={app_context['form_id']}, "
        f"StudyID={app_context['community_id']}"
    )

    # 2. Transform your Spec to the iMednet Layout
    # Create a simple Layout with the spec data
    # Here we create a single page with a single row containing a text field

    # Generate a unique field ID or use one from spec
    field_id = f"fld_{int(time.time())}"

    text_field = Entity(
        id=field_id,
        props=TextFieldProps(
            type="text",
            label=spec_data.get("question", "New Question"),
            length=50,
            fld_id=field_id,
            question_id=field_id,  # Usually needs to be unique
            question_name="NEW_Q",
        ),
    )

    table_entity = Entity(
        id=f"tbl_{int(time.time())}",
        props=TableProps(type="table", columns=1),
        rows=[Row(cols=[Col(entities=[text_field])])],
    )

    layout = Layout(pages=[Page(entities=[table_entity])])

    # 3. Send the Data via API (Using the SDK Client)
    client = FormDesignerClient(base_url=app_context["base_url"], phpsessid=phpsessid)

    try:
        print(">>> 🚀 Sending payload via FormDesignerClient...")
        response_text = client.save_form(
            csrf_key=app_context["csrf_token"],
            form_id=int(app_context["form_id"]),
            community_id=int(app_context["community_id"]),
            revision=int(app_context["revision"]),
            layout=layout,
        )
        print(">>> ✅ Form Updated Successfully!")
        print(f">>> Server Response: {response_text[:100]}...")  # Truncate for display

        # Reload to show changes
        print(">>> 🔄 Reloading page...")
        page.reload()

    except Exception as e:
        print(f">>> ❌ Error saving form: {e}")


def run_hybrid_mode():
    # We use a persistent_context so your login is saved between runs!
    user_data_dir = "./browser_session"

    with sync_playwright() as p:
        # Launch Chrome (Not Headless)
        print(">>> Launching Browser...")
        browser = p.chromium.launch_persistent_context(
            user_data_dir,
            headless=False,
            args=["--start-maximized"],  # easier for the human
            channel="chrome",  # Use installed chrome if available, else chromium
        )

        page = browser.pages[0] if browser.pages else browser.new_page()

        # 1. Initial Nav (Optional - just to be helpful)
        if "imednet.com" not in page.url:
            try:
                page.goto("https://www.imednet.com/")
            except Exception:
                pass  # Might fail if offline or bad URL, just let user drive

        # 2. THE HUMAN LOOP
        print("-------------------------------------------------")
        print("👨‍💻 HUMAN TASK:")
        print("1. Log in (if not already).")
        print("2. Navigate to the Form Designer for the specific form.")
        print("3. Ensure you are ready to inject the new design.")
        print("-------------------------------------------------")

        # Wait for user input in the console to trigger the automation
        input(">>> PRESS ENTER HERE WHEN READY TO INJECT SPECIFICATION <<<")

        # 3. Load your external specification
        # In a real app, this might open a file picker
        mock_spec = {"question": "Did you take the medication?", "type": "text"}

        # 4. Run the injection
        try:
            inject_form_specification(page, mock_spec)
        except Exception as e:
            print(f">>> ❌ Unexpected Error: {e}")

        # Keep browser open for inspection
        print(">>> Done. You can close the browser manually.")
        input("Press Enter to close script...")
        browser.close()


if __name__ == "__main__":
    run_hybrid_mode()
