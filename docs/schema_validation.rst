Schema Validation Flow
======================

The SDK uses :class:`~imednet.validation.schema.SchemaValidator` and
:class:`~imednet.validation.schema.SchemaCache` to verify record data before
submitting it to the API. The validator checks that all variables exist,
required fields are present, and that values match the expected types.
If the variable metadata for a form is missing, ``SchemaValidator`` automatically
loads it from the API using :class:`~imednet.endpoints.variables.VariablesEndpoint`.
Any problems raise :class:`~imednet.core.exceptions.ValidationError` before the
record is sent to the server.

The diagram below outlines the main steps.

.. mermaid::

   graph TD
       A[Record payload] --> B[SchemaValidator.validate_record]
       B --> C{formKey or formId}
       C -->|Resolve formKey| D[SchemaCache]
       D --> E{variables cached?}
       E -- No --> F[refresh(study_key)]
       F --> G[sdk.variables.list]
       G --> D
       E -- Yes --> H[validate_record_data]
       D --> H
       H --> I{validation passes?}
       I -- Yes --> J[submit to RecordsEndpoint]
   I -- No --> K[raise ValidationError]

Record payloads can also be validated asynchronously. Use
``AsyncSchemaValidator.validate_batch`` with ``AsyncImednetSDK`` before
submitting records::

    async with AsyncImednetSDK() as sdk:
        validator = AsyncSchemaValidator(sdk)
        await validator.validate_batch(study_key, records)
        await sdk.records.async_create(study_key, records, schema=validator.schema)
