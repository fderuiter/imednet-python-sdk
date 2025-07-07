Schema Validation Flow
======================

The SDK uses :class:`~imednet.validation.cache.SchemaValidator` and
:class:`~imednet.validation.cache.SchemaCache` to verify record data before
submitting it to the API. The validator checks that all variables exist,
required fields are present, and that values match the expected types.
If the variable metadata for a form is missing, ``SchemaValidator`` automatically
loads it from the API using :class:`~imednet.endpoints.variables.VariablesEndpoint`.
Any problems raise :class:`~imednet.core.exceptions.ValidationError` before the
record is sent to the server.

``SchemaValidator`` works with both synchronous and asynchronous SDK clients.
It refreshes cached metadata using the appropriate API calls depending on the
client type.

The diagram below outlines the main steps.

.. mermaid::

   graph TD
       A[Record payload] --> B[SchemaValidator.validate_record]
       B --> C{formKey or formId}
       C -->|Resolve formKey| D[SchemaCache]
       D --> E{variables cached?}
       E -- No --> F["refresh(study_key)"]
       F --> G[sdk.variables.list]
       G --> D
       E -- Yes --> H[validate_record_data]
       D --> H
       H --> I{validation passes?}
       I -- Yes --> J[submit to RecordsEndpoint]
   I -- No --> K[raise ValidationError]

Record payloads can also be validated asynchronously. Use
``SchemaValidator.validate_batch`` with ``AsyncImednetSDK`` before
submitting records::

    async with AsyncImednetSDK() as sdk:
        validator = SchemaValidator(sdk)
        await validator.validate_batch(study_key, records)
        await sdk.records.async_create(study_key, records, schema=validator.schema)

Offline Example
---------------

``imednet.testing.fake_data`` provides helpers for generating form
metadata and sample records without an API connection. Combine these
functions with ``SchemaCache`` to validate payloads locally::

    from types import SimpleNamespace
    from imednet.testing import fake_data
    from imednet.validation.cache import SchemaCache

    forms = fake_data.fake_forms_for_cache(1, study_key="S")
    variables = fake_data.fake_variables_for_cache(forms, vars_per_form=2,
                                                   study_key="S")

    forms_ep = SimpleNamespace(list=lambda **_: forms)
    vars_ep = SimpleNamespace(list=lambda form_id=None, **__: [
        v for v in variables if form_id is None or v.form_id == form_id
    ])

    schema = SchemaCache()
    schema.refresh(forms_ep, vars_ep, study_key="S")

    record = fake_data.fake_record(schema)
