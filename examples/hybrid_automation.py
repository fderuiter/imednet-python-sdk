from typing import Any, Dict, List

from playwright.sync_api import sync_playwright

from imednet.form_designer.models import (
    Col,
    DateTimeFieldProps,
    Entity,
    LabelProps,
    Layout,
    Page,
    Row,
    TableProps,
    TextFieldProps,
)


def generate_form_payload(
    form_id: str, csrf_key: str, community_id: str, revision: str, spec_data: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Generates the exact HTTP POST body required by iMednet's formdez_save.php.
    Constructs the Layout object using Pydantic models and serializes it.
    """
    rows = []

    for field in spec_data:
        # Create a Label Column
        label_entity = Entity(
            id=f"gen_{field['id']}_lbl",
            props=LabelProps(
                type="label",
                label=f"<p><strong>{field['label']}</strong></p>",
                label_id=f"lbl_{field['id']}",
            ),
        )

        # Create an Input Column
        f_type = field.get("type", "text")
        props = None

        # Map simple types to specific Props models
        if f_type == "text":
            props = TextFieldProps(
                type="text",
                question_name=field["variable_name"],
                question_id=field["id"],
                fld_id=field["id"],
                length=field.get("length", 50),
            )
        elif f_type == "datetime":
            props = DateTimeFieldProps(
                type="datetime",
                question_name=field["variable_name"],
                question_id=field["id"],
                fld_id=field["id"],
                # Default settings for date/time
                date_ctrl=1,
                time_ctrl=0,
            )
        else:
            # Fallback for now to text if unknown
            props = TextFieldProps(
                type="text",
                question_name=field["variable_name"],
                question_id=field["id"],
                fld_id=field["id"],
                length=50,
            )

        input_entity = Entity(id=f"gen_{field['id']}_inp", props=props)

        # Add to Row (Label Col + Input Col)
        rows.append(Row(cols=[Col(entities=[label_entity]), Col(entities=[input_entity])]))

    # Construct the full Page Layout
    # We wrap everything in a Table for alignment
    root_table = Entity(id="root_table", props=TableProps(type="table", columns=2), rows=rows)

    layout_obj = Layout(pages=[Page(entities=[root_table])])

    # Serialize Layout to JSON string
    layout_json = layout_obj.model_dump_json(exclude_none=True)

    # Construct the Final Body Payload
    payload = {
        "CSRFKey": csrf_key,
        "resubmit": "0",
        "__internal_form_url": "/app/formdez/formdez_save.php",
        "form_id": str(form_id),
        "lang_id": "1",
        "community_id": str(community_id),
        "quick_save": "1",
        "revision": str(revision),
        "layout": layout_json,  # The magic string
        "__internal_ajax_request": "1",
    }

    return payload


def inject_form_specification(page, spec_data: List[Dict[str, Any]]):
    """
    This function runs once the human has navigated to the designer.
    It scrapes the necessary tokens and uses the API to update the form.
    """
    print(">>> 🤖 AUTOMATION ENGAGED")

    # 1. Scrape the "Hidden" Context from the Page
    app_context = page.evaluate(
        """() => {
        const getValue = (selector) => document.querySelector(selector)?.value;
        const urlParams = new URLSearchParams(window.location.search);

        return {
            csrf_token: getValue('input[name="CSRFKey"]') || getValue('#CSRFKey'),
            form_id: urlParams.get('formId') || getValue('input[name="form_id"]'),
            community_id: getValue('input[name="community_id"]'),
            revision: getValue('input[name="revision"]'),
        }
    }"""
    )

    # Verify we have all required fields
    required_fields = ["csrf_token", "form_id", "community_id", "revision"]
    missing_fields = [f for f in required_fields if not app_context.get(f)]

    if missing_fields:
        print(f">>> ❌ Error: Could not scrape: {', '.join(missing_fields)}")
        print(">>> Please ensure you are on the Form Designer page.")
        return

    print(
        f">>> Captured Context: FormID={app_context['form_id']}, "
        f"StudyID={app_context['community_id']}, Rev={app_context['revision']}"
    )

    # 2. Generate Payload
    try:
        payload = generate_form_payload(
            form_id=app_context["form_id"],
            csrf_key=app_context["csrf_token"],
            community_id=app_context["community_id"],
            revision=app_context["revision"],
            spec_data=spec_data,
        )
    except Exception as e:
        print(f">>> ❌ Error generating payload: {e}")
        return

    # 3. Send the Data via Playwright Request (reuses browser context/cookies)
    url = f"{page.url.split('/app/')[0]}/app/formdez/formdez_save.php"
    print(f">>> 🚀 Sending payload to {url}...")

    try:
        # page.request uses the browser context, so cookies are included automatically
        response = page.request.post(
            url,
            data=payload,
            headers={
                "X-Requested-With": "XMLHttpRequest",
                "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            },
        )

        if response.ok:
            print(">>> ✅ Form Updated Successfully!")
            print(f">>> Server Response: {response.text()[:100]}...")

            # Reload to show changes
            print(">>> 🔄 Reloading page...")
            page.reload()
        else:
            print(f">>> ❌ Server returned error: {response.status} {response.status_text}")
            print(response.text())

    except Exception as e:
        print(f">>> ❌ Error sending request: {e}")


def run_hybrid_mode():
    # We use a persistent_context so your login is saved between runs!
    user_data_dir = "./browser_session"

    with sync_playwright() as p:
        # Launch Chrome (Not Headless)
        print(">>> Launching Browser...")
        browser = p.chromium.launch_persistent_context(
            user_data_dir,
            headless=False,
            args=["--start-maximized"],
            channel="chrome",
        )

        page = browser.pages[0] if browser.pages else browser.new_page()

        # 1. Initial Nav
        if "imednet.com" not in page.url:
            try:
                page.goto("https://www.imednet.com/")
            except Exception:
                pass

        # 2. THE HUMAN LOOP
        print("-------------------------------------------------")
        print("👨‍💻 HUMAN TASK:")
        print("1. Log in (if not already).")
        print("2. Navigate to the Form Designer for the specific form.")
        print("3. Ensure you are ready to inject the new design.")
        print("-------------------------------------------------")

        input(">>> PRESS ENTER HERE WHEN READY TO INJECT SPECIFICATION <<<")

        # 3. Load your external specification
        # Example Spec matching the user's request
        mock_spec = [
            {
                "id": 105803,
                "label": "Subject Initials",
                "variable_name": "SUBINIT",
                "type": "text",
            },
            {
                "id": 105804,
                "label": "Date of Visit",
                "variable_name": "VISDAT",
                "type": "datetime",
            },
        ]

        # 4. Run the injection
        try:
            inject_form_specification(page, mock_spec)
        except Exception as e:
            print(f">>> ❌ Unexpected Error: {e}")

        print(">>> Done. You can close the browser manually.")
        input("Press Enter to close script...")
        browser.close()


if __name__ == "__main__":
    run_hybrid_mode()
