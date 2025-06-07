Veeva Push Workflow
===================

The :class:`~imednet.workflows.veeva_push.VeevaPushWorkflow` provides a
straightforward way to validate and send iMednet record data to Veeva Vault.
It supports bulk upsert with automatic splitting into batches of up to
``500`` records and staging of attachment fields. An asynchronous variant
:class:`~imednet.workflows.veeva_push.AsyncVeevaPushWorkflow` allows
concurrent processing using a configurable semaphore to limit the number
of simultaneous requests.

Example usage::

   from imednet.veeva import VeevaVaultClient
   from imednet.workflows.veeva_push import VeevaPushWorkflow

   client = VeevaVaultClient(
       vault="myvault",
       client_id="<id>",
       client_secret="<secret>",
       username="user",
       password="pass",
   )
   client.authenticate()

   workflow = VeevaPushWorkflow(client)
   record = {"name__v": "Sample", "status__v": "New"}
   workflow.push_record("prod__c", record)

   # Bulk upload with attachments
   records = [
       {"name__v": "A", "file__c": "/tmp/a.pdf"},
       {"name__v": "B", "file__c": "/tmp/b.pdf"},
   ]
   workflow.push_records_bulk(
       "prod__c",
       records,
       attachment_fields=["file__c"],
       id_param="name__v",
       batch_size=200,
   )

Async usage::

   from imednet.veeva import AsyncVeevaVaultClient
   from imednet.workflows.veeva_push import AsyncVeevaPushWorkflow

   client = AsyncVeevaVaultClient(
       vault="myvault",
       client_id="<id>",
       client_secret="<secret>",
       username="user",
       password="pass",
   )
   await client.authenticate()

   workflow = AsyncVeevaPushWorkflow(client, concurrency=10)
   await workflow.push_records_bulk(
       "prod__c",
       records,
       attachment_fields=["file__c"],
       id_param="name__v",
       batch_size=200,
   )

The workflow uses
:func:`~imednet.veeva.validate_record_for_upsert` to ensure that records
contain required fields and valid picklist values before calling
:meth:`~imednet.veeva.VeevaVaultClient.upsert_object`.

