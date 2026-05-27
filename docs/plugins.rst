Plugin Authoring Guide
======================

The iMednet SDK ships two first-party optional plugins:

* :ref:`imednet-streamlit <streamlit-dashboard-plugin>` — interactive Streamlit
  reporting dashboards.
* ``imednet-workflows`` — opinionated data-extraction and query-management
  workflows (see the workflows API reference).

The built-in ``imednet-workflows`` package is the reference implementation for
third-party plugins.  Any third-party package can register its own plugin using
the standard `Python entry-point`_ mechanism.

.. _Python entry-point: https://packaging.python.org/en/latest/specifications/entry-points/

.. _streamlit-dashboard-plugin:

Streamlit Dashboard Plugin (``imednet-streamlit``)
---------------------------------------------------

The ``imednet-streamlit`` package provides a multi-page Streamlit reporting
dashboard that consumes the core SDK.  It is intentionally isolated so that
users deploying the SDK in serverless or batch environments are not forced to
install the large ``streamlit`` and ``altair`` binaries.

For the full end-user walkthrough and configuration reference, see the
`Streamlit plugin guide <plugins/streamlit.md>`_.

Installation
~~~~~~~~~~~~

.. code-block:: bash

   pip install imednet-streamlit

Or, when working inside the monorepo:

.. code-block:: bash

   pip install ./packages/plugins-streamlit

Launching the dashboard
~~~~~~~~~~~~~~~~~~~~~~~

Once installed, the ``imednet dashboard`` CLI command becomes available:

.. code-block:: bash

   imednet dashboard

This boots a local Streamlit server (default port **8501**) and opens the
dashboard in your default browser.

Optional flags:

.. code-block:: bash

   imednet dashboard --port 8080        # use a custom port
   imednet dashboard --no-browser       # suppress automatic browser launch

If the plugin is **not** installed, the command exits with code ``1`` and
prints a helpful message:

.. code-block:: text

   Dashboard plugin not found. Install it with:
     pip install imednet-streamlit

You can also launch the app directly with Streamlit:

.. code-block:: bash

   streamlit run "$(python -c 'import imednet_streamlit.app as app; print(app.__file__)')"

Dashboard pages
~~~~~~~~~~~~~~~

+----------------------+------------------------------------------------------+
| Page                 | Description                                          |
+======================+======================================================+
| Home                 | Connection status and navigation guide               |
+----------------------+------------------------------------------------------+
| Query Status         | Open/closed query breakdown with trend charts        |
+----------------------+------------------------------------------------------+
| Subject Enrollment   | Enrollment funnel and site-level summaries           |
+----------------------+------------------------------------------------------+
| Site Performance     | Site-level query rate metrics and rankings           |
+----------------------+------------------------------------------------------+
| Data Completeness    | Record status heatmap and form-level summaries       |
+----------------------+------------------------------------------------------+

Credential management
~~~~~~~~~~~~~~~~~~~~~

Credentials are entered in the sidebar at runtime.  The API Key and Security
Key fields use ``type="password"`` so they are masked in the browser.  Values
are stored in ``st.session_state`` only for the lifetime of the browser
session and are never logged, written to disk, or exposed in plaintext.

After clicking **Connect**, the credential keys are removed from
``st.session_state`` and only the constructed ``ImednetSDK`` instance is
retained for subsequent API calls.

Architecture rules
~~~~~~~~~~~~~~~~~~

* **SDK-only data access** — dashboard pages never call ``requests`` or
  ``httpx`` directly; all network calls go through ``ImednetSDK``, which
  provides the built-in retry policies and error handling.
* **Caching** — every ``_fetch_*`` function is decorated with
  ``@st.cache_data(ttl=600)`` to prevent API rate-limiting on re-renders.
* **Zero core bloat** — ``streamlit``, ``altair``, and ``pandas`` do **not**
  appear in the ``packages/core`` dependency list.

Workbench MVP developer guide
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The Reporting Foundation MVP pages (Setup Wizard, Review Workbench, Publisher
Wizard, Data Lineage) are designed so teams can extend templates and schema
mapping safely without changing the core SDK package.

Extending templates and schema mappings
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Use :class:`imednet.models.study_config.StudyConfiguration` as the single
source of truth for extension points:

* ``mappings`` defines canonical-field to raw-form mappings.
* ``terminology_lookups`` defines normalization tables used before validation.
* ``widgets`` defines dashboard template blocks rendered by the MVP pages.

When introducing new mappings or widgets, validate behavior in both:

* ``tests/unit/streamlit/`` for UI interaction and page-state checks.
* ``tests/unit/workflows/`` for schema profiling/extraction behavior.

Headless Streamlit testing pattern (AppTest)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Use Streamlit's official ``AppTest`` runner to test full-page flows without
manual ``sys.modules`` monkeypatching:

.. code-block:: python

   from pathlib import Path
   from streamlit.testing.v1 import AppTest
   from unittest.mock import patch

   APP_PATH = (
       Path(__file__).resolve().parents[3]
       / "packages"
       / "plugins-streamlit"
       / "src"
       / "imednet_streamlit"
       / "app.py"
   )

   def test_dashboard_login_flow() -> None:
       with patch("imednet_streamlit.auth.ImednetSDK") as mock_sdk:
           mock_sdk.return_value = object()
           at = AppTest.from_file(str(APP_PATH))
           at.run()
           at.sidebar.text_input(key="_imednet_api_key").input("test-api-key")
           at.sidebar.text_input(key="_imednet_security_key").input("test-security-key")
           at.sidebar.text_input(key="_imednet_study_key").input("PROT-100")
           at.sidebar.button[0].click()
           at.run()
           assert at.sidebar.success[0].value == "Connected ✓"

Optional-plugin CLI graceful-degradation verification
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

CLI commands that depend on optional plugins should be tested in two modes:

* **Plugin present**: patch ``importlib.util.find_spec`` (or module import) to
  return a module and assert the command runs.
* **Plugin absent**: patch discovery to return ``None`` (or raise
  ``ImportError``) and assert the command exits with code ``1`` and prints
  install guidance.

See ``tests/unit/cli/test_cli.py`` and ``tests/unit/cli/test_cli_export.py``
for repository examples of this pattern.

Plugin authoring reference
--------------------------

How it works
------------

During :class:`~imednet.sdk.ImednetSDK` (and
:class:`~imednet.sdk.AsyncImednetSDK`) initialisation the SDK queries the
``imednet.plugins`` entry-point group for an entry named ``"workflows"``.  If
exactly one is found the SDK loads the factory callable and calls it with
itself as the argument.  The returned object is stored as ``sdk.workflows``.

If the plugin is **not** installed, ``sdk.workflows`` is a placeholder that
raises :exc:`ImportError` with a helpful message on first attribute access.

If the plugin **is** installed but fails to load (broken import, wrong
interface, …) a :exc:`~imednet.errors.PluginLoadError` is raised at SDK
construction time.

Plugin contract
---------------

A plugin package must expose a single factory callable.  The factory must
satisfy :class:`~imednet.plugins.PluginProtocol`:

.. code-block:: python

    from typing import Protocol
    from imednet.plugins import PluginProtocol, WorkflowsNamespaceProtocol

    class PluginProtocol(Protocol):
        def __call__(self, sdk_instance: Any) -> WorkflowsNamespaceProtocol: ...

The object returned by the factory must satisfy
:class:`~imednet.plugins.WorkflowsNamespaceProtocol` — it must expose at
least the following attributes (any type):

* ``data_extraction``
* ``query_management``
* ``record_mapper``
* ``record_update``
* ``subject_data``

Minimal working example
-----------------------

.. code-block:: python

    # myplugin/namespace.py
    from __future__ import annotations

    from typing import TYPE_CHECKING, Any

    if TYPE_CHECKING:
        from imednet.sdk import ImednetSDK


    class MyDataExtraction:
        def __init__(self, sdk: "ImednetSDK") -> None:
            self._sdk = sdk

        def run(self, study_key: str) -> list[Any]:
            return self._sdk.records.list(study_key=study_key)


    class MyWorkflows:
        def __init__(self, sdk: "ImednetSDK") -> None:
            self.data_extraction = MyDataExtraction(sdk)
            self.query_management = None   # implement as needed
            self.record_mapper = None
            self.record_update = None
            self.subject_data = None


    def create_workflows(sdk: "ImednetSDK") -> MyWorkflows:
        """Entry-point factory — called by ImednetSDK at initialisation."""
        return MyWorkflows(sdk)

Registering the entry point
---------------------------

Add the following to your package's ``pyproject.toml``:

.. code-block:: toml

    [tool.poetry.plugins."imednet.plugins"]
    workflows = "myplugin.namespace:create_workflows"

Or, when using ``setuptools``, in ``setup.cfg``:

.. code-block:: ini

    [options.entry_points]
    imednet.plugins =
        workflows = myplugin.namespace:create_workflows

Once installed (e.g. ``pip install myplugin``), the SDK will discover and
load the plugin automatically:

.. code-block:: python

    from imednet import ImednetSDK

    sdk = ImednetSDK(api_key="...", security_key="...")
    records = sdk.workflows.data_extraction.run("MY_STUDY")

Error handling
--------------

:exc:`~imednet.errors.PluginLoadError` is raised when:

* More than one ``"workflows"`` plugin is registered in the
  ``imednet.plugins`` entry-point group.
* The entry point fails to import (e.g. broken dependency).
* The loaded object is not callable.
* The factory raises :exc:`TypeError` when called with the SDK instance.

:exc:`~imednet.errors.PluginLoadError` is a subclass of
:exc:`~imednet.errors.ImednetError` so it can be caught uniformly:

.. code-block:: python

    from imednet import ImednetSDK
    from imednet.errors import ImednetError

    try:
        sdk = ImednetSDK(api_key="...", security_key="...")
    except ImednetError as exc:
        print(f"SDK initialisation failed: {exc}")

API reference
-------------

.. autoclass:: imednet.plugins.PluginProtocol
   :members:
   :undoc-members:

.. autoclass:: imednet.plugins.WorkflowsNamespaceProtocol
   :members:
   :undoc-members:

.. autoexception:: imednet.errors.PluginLoadError
