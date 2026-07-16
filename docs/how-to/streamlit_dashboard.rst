==========================================
Streamlit Dashboard Installation and Usage
==========================================

``imednet-streamlit`` provides interactive operational dashboards for iMednet EDC studies.

Installation
------------

Prerequisites
^^^^^^^^^^^^^

- Python 3.10+
- Core SDK installed (``imednet``)
- Streamlit plugin installed (``imednet-streamlit``)

Quick Start
^^^^^^^^^^^

.. code-block:: bash

    pip install imednet-streamlit
    imednet dashboard
    imednet dashboard --port 9999
    imednet dashboard --no-browser


Authentication
--------------

Use the sidebar to connect:

1. Enter API Key (masked)
2. Enter Security Key (masked)
3. Enter Study Key
4. Click **Connect**

Using Streamlit Secrets (for shared deployments)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: toml

    # .streamlit/secrets.toml (DO NOT COMMIT)
    [imednet]
    api_key = "your-api-key"
    security_key = "your-security-key"


``.streamlit/secrets.toml`` is already ignored by this repository's ``.gitignore``;
keep credentials in that file only for local/shared deployment configuration and
never commit secret values.

Deployment
----------

Local
^^^^^
- Install plugin and run ``imednet dashboard``.
- Provide credentials in the sidebar at runtime.

Streamlit Community Cloud
^^^^^^^^^^^^^^^^^^^^^^^^^
- Add plugin dependencies to the deployed environment.
- Configure credentials with Streamlit secrets.
