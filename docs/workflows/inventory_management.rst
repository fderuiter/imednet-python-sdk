InventoryManagementWorkflow
==========================

The :class:`~imednet.workflows.inventory_management.InventoryManagementWorkflow`
provides a helper to fetch all device catalog records for a study.

List catalog items
------------------

``list_catalog_items`` builds a filter using ``recordType=CATALOG`` and any
additional criteria you provide, then calls the SDK's ``records.list`` method::

   from imednet.sdk import ImednetSDK
   from imednet.workflows.inventory_management import InventoryManagementWorkflow

   sdk = ImednetSDK(api_key="<API>", security_key="<SEC>")
   wf = InventoryManagementWorkflow(sdk)
   items = wf.list_catalog_items("MY_STUDY")
   print(items)
