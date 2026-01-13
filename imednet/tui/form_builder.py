from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

from textual import work
from textual.containers import Container, VerticalScroll
from textual.widgets import (
    Button,
    Input,
    Label,
    Log,
    Select,
)

from imednet.form_designer import PRESETS, FormBuilder, FormDesignerClient

if TYPE_CHECKING:
    from imednet.sdk import ImednetSDK


class FormBuilderPane(Container):
    """Pane for building and submitting forms via legacy endpoint."""

    DEFAULT_CSS = """
    FormBuilderPane {
        layout: vertical;
        padding: 1;
    }
    FormBuilderPane Input {
        margin-bottom: 1;
    }
    FormBuilderPane Select {
        margin-bottom: 1;
    }
    FormBuilderPane Button {
        margin-top: 1;
        width: 100%;
        background: $primary;
    }
    """

    def __init__(self, sdk: ImednetSDK, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.sdk = sdk

    def compose(self) -> Any:
        base_url = getattr(self.sdk, "_base_url", "")

        with VerticalScroll():
            yield Label("Target Environment")
            yield Input(value=base_url, placeholder="Base URL", id="fb_base_url")

            yield Label("Session Credentials (from browser)")
            yield Input(placeholder="PHPSESSID", id="fb_phpsessid", password=True)
            yield Input(placeholder="CSRFKey", id="fb_csrf")

            yield Label("Target Context")
            yield Input(placeholder="Form ID (e.g., 10351)", id="fb_form_id", type="integer")
            yield Input(placeholder="Community ID (e.g., 500)", id="fb_comm_id", type="integer")
            yield Input(placeholder="Next Revision (e.g., 3)", id="fb_revision", type="integer")

            yield Label("Form Definition")
            # Select options must be (label, value)
            options = [(k, k) for k in PRESETS.keys()]
            yield Select(options, prompt="Select a Preset", id="fb_preset")

            yield Button("Build & Submit Payload", variant="primary", id="fb_submit")

    @work(exclusive=True, thread=True)
    def submit_form(
        self,
        base_url: str,
        phpsessid: str,
        csrf: str,
        form_id: int,
        comm_id: int,
        rev: int,
        preset_name: str
    ) -> None:
        logger = logging.getLogger("imednet")
        logger.info(f"Starting Form Build: {preset_name} -> {base_url}")

        try:
            # 1. Build Layout
            builder = FormBuilder()
            build_func = PRESETS[preset_name]
            build_func(builder)
            layout = builder.build()
            logger.info("Layout generated successfully.")

            # 2. Submit
            client = FormDesignerClient(base_url, phpsessid)
            logger.info("Submitting payload to formdez_save.php...")

            response_text = client.save_form(
                csrf_key=csrf,
                form_id=form_id,
                community_id=comm_id,
                revision=rev,
                layout=layout
            )

            logger.info("Submission Complete!")
            # Truncate response if too long
            snippet = response_text[:200] + "..." if len(response_text) > 200 else response_text
            logger.info(f"Server Response: {snippet}")

            self.app.notify("Form Submitted Successfully!", severity="information")

        except Exception as e:
            logger.error(f"Error submitting form: {e}")
            self.app.notify(f"Error: {e}", severity="error")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "fb_submit":
            # Gather inputs
            base_url = self.query_one("#fb_base_url", Input).value
            phpsessid = self.query_one("#fb_phpsessid", Input).value
            csrf = self.query_one("#fb_csrf", Input).value

            # Inputs with type="integer" are still returning str in .value, validation handled by widget?
            # Actually Textual's Input with type='integer' restricts input but .value is str.
            # We need to parse.
            try:
                form_id = int(self.query_one("#fb_form_id", Input).value)
                comm_id = int(self.query_one("#fb_comm_id", Input).value)
                rev = int(self.query_one("#fb_revision", Input).value)
            except ValueError:
                self.app.notify("Please enter valid integers for IDs/Revision", severity="error")
                return

            preset_sel = self.query_one("#fb_preset", Select)
            if preset_sel.value == Select.BLANK:
                self.app.notify("Please select a form preset", severity="error")
                return
            preset = str(preset_sel.value)

            if not phpsessid or not csrf:
                self.app.notify("Session ID and CSRF Key are required", severity="error")
                return

            self.submit_form(base_url, phpsessid, csrf, form_id, comm_id, rev, preset)
