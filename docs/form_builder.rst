Form Builder
============

The Form Builder module allows you to programmatically define form layouts and submit them to the legacy iMedNet Form Designer. This bypasses manual drag-and-drop operations, enabling automated form creation and updates.

.. warning::
    This module interacts with the legacy Form Designer endpoint (``formdez_save.php``). It requires session credentials (``PHPSESSID`` and ``CSRFKey``) scraped from an active browser session.

Core Concepts
-------------

The module mimics the "State Dump" architecture of the Form Designer:

1.  **Layout Definition**: You define the form structure (Pages, Sections, Fields) using Python code.
2.  **Serialization**: The code converts this definition into the complex JSON hierarchy expected by the server.
3.  **Submission**: The payload is POSTed to the legacy endpoint using your browser cookies.

.. note::
    This approach is "destructive" in the sense that it overwrites the current page state with the new layout. Always ensure you are working on the correct Revision number.

Usage
-----

The primary way to use the Form Builder is via the **Textual TUI** or the **Hybrid Script**.

TUI (Interactive)
~~~~~~~~~~~~~~~~~

Launch the TUI and navigate to the "Form Builder" tab:

.. code-block:: console

    imednet tui

The TUI provides a dashboard to:
1.  Enter your Session Credentials (PHPSESSID, CSRFKey).
2.  Configure target parameters (Form ID, Community ID, Revision).
3.  Select a "Preset" (a pre-defined Python function that builds a specific form).
4.  Execute the build and submission in the background.

Hybrid Script (Headless)
~~~~~~~~~~~~~~~~~~~~~~~~

For CI/CD or automated workflows, use the example script:

.. code-block:: console

    python examples/build_form_payload.py --preset "Demo Form" \
        --base-url "https://your.imednet.com" \
        --phpsessid "YOUR_SESSION_ID" \
        --csrf "YOUR_CSRF_KEY" \
        --form-id 12345 \
        --comm-id 999 \
        --revision 5

Presets
-------

Forms are defined as "Presets" in ``imednet/builders/presets.py``. A preset is simply a function that accepts a ``FormBuilder`` instance.

.. code-block:: python

    def build_my_form(builder: FormBuilder) -> None:
        builder.add_section_header("My New Section")

        builder.add_field(
            type="text",
            label="Subject Initials",
            question_name="INIT",
            required=True
        )

See ``imednet.builders.presets`` for more examples.

API Reference
-------------

.. toctree::
   :maxdepth: 2

   imednet.models.form_designer
   imednet.builders.form_builder
   imednet.endpoints.form_designer
