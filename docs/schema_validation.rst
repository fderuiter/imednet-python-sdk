Schema Validation Flow
======================

The SDK uses :class:`~imednet.validation.schema.SchemaValidator` and
:class:`~imednet.validation.schema.SchemaCache` to verify record data before
submitting it to the API. The diagram below outlines the main steps.

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
