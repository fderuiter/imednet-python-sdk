Terminal User Interface (TUI)
=============================

The imednet SDK includes a rich Terminal User Interface (TUI) powered by Textual. This interface allows for interactive exploration of the API, data visualization, and even form design, all from the command line.

Launching the TUI
-----------------

To start the TUI, simply run:

.. code-block:: bash

    imednet tui

Navigation
----------

The TUI is organized into tabs or panes, accessible via the sidebar or keyboard shortcuts.

*   **Dashboard**: Overview of available studies and quick stats.
*   **Studies**: List of studies with detailed views.
*   **Subjects**: Interactive table of subjects with filtering.
*   **Records**: Browse clinical data records.
*   **Form Builder**: A visual interface for designing and validating CRF forms.
*   **Logs**: Real-time view of SDK logs.

Features
--------

Data Exploration
~~~~~~~~~~~~~~~~

*   **Interactive Tables**: Sort and filter data directly in the terminal.
*   **Detail Views**: Inspect JSON responses and nested data structures.
*   **Study Context**: Switch between studies easily.

Form Builder
~~~~~~~~~~~~

The Form Builder pane allows you to construct form definitions using the :mod:`imednet.form_designer` models.

*   **Visual Structure**: See the hierarchy of your form (Table -> Row -> Column -> Field).
*   **Property Editing**: Edit field properties (labels, types, validation rules).
*   **Preview**: See a representation of how the form might look.
*   **JSON Export**: Generate the JSON payload required for the API.

Logging
~~~~~~~

The Logs pane captures standard Python logs emitted by the SDK. This is useful for debugging API calls, tracking retries, and inspecting authentication flow without leaving the interface.
