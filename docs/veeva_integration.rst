Veeva Vault Integration
=======================

The SDK provides a bridge to transfer data from iMednet to Veeva Vault. This integration allows you to export clinical data (Subjects, Visits, Forms, etc.) from an iMednet study and import it into Veeva Vault as object records or documents.

.. note::
   This feature is currently in development. The API described below is subject to change.

Prerequisites
-------------

*   Active iMednet API access (API Key, Security Key).
*   Veeva Vault account with API access enabled.
*   A Vault user with permissions to create/update the target objects (e.g., ``Subject__v``, ``Visit__v``).

Installation
------------

The Veeva integration is part of the ``imednet`` package but requires no extra dependencies beyond the standard SDK installation.

.. code-block:: bash

   pip install imednet

Configuration
-------------

You must configure connection details for both iMednet and Veeva Vault.

iMednet Configuration
~~~~~~~~~~~~~~~~~~~~~

Follow the standard :doc:`configuration` guide to set up your iMednet credentials.

Veeva Vault Configuration
~~~~~~~~~~~~~~~~~~~~~~~~~

You can provide Veeva credentials directly to the bridge or set them as environment variables:

*   ``VEEVA_VAULT_URL``: The base URL of your Vault (e.g., ``https://myvault.veevavault.com``).
*   ``VEEVA_USERNAME``: Your Vault username.
*   ``VEEVA_PASSWORD``: Your Vault password.
*   ``VEEVA_CLIENT_ID``: (Optional) A custom client ID for tracking API usage.

Usage
-----

The primary interface is the ``VeevaVaultBridge`` class in ``imednet.integrations.veeva``.

Basic Export
~~~~~~~~~~~~

Here is a simple example of exporting all subjects from an iMednet study to a Veeva Vault ``Study_Subject__v`` object.

.. code-block:: python

   import os
   from imednet import ImednetSDK
   from imednet.integrations.veeva import VeevaVaultBridge

   # Initialize SDK
   sdk = ImednetSDK(api_key="...", security_key="...")

   # Initialize Bridge
   bridge = VeevaVaultBridge(
       vault_url="https://myvault.veevavault.com",
       username=os.getenv("VEEVA_USERNAME"),
       password=os.getenv("VEEVA_PASSWORD")
   )

   # Run the export
   result = bridge.export_subjects(
       sdk=sdk,
       study_key="MY_STUDY_KEY",
       target_object="Study_Subject__v",
       mapping={
           "subject_id": "name__v",
           "site_id": "site__v"
       }
   )

   print(f"Exported {result.success_count} records to Veeva Vault.")

Data Mapping
------------

The bridge supports custom field mapping. You can provide a dictionary where keys are iMednet field names and values are Veeva Vault field API names.

Supported Data Types
--------------------

*   **Subjects**: Maps iMednet subjects to Vault objects.
*   **Visits**: Maps iMednet visits to Vault objects.
*   **Forms**: Maps iMednet form data to Vault objects.

Error Handling
--------------

The bridge will raise ``VeevaIntegrationError`` if connection fails or if Vault returns an error response. Partial failures (e.g., some records failed to import) are reported in the result object.
