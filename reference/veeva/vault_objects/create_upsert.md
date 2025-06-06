# Create & Upsert Object Records

Create or upsert Vault object records in bulk. This endpoint can also be used to create User Tasks or User (user__sys) records.

## Request

```bash
curl -X POST -H "Authorization: {SESSION_ID}" \
-H "Content-Type: text/csv" \
-H "Accept: text/csv" \
--data-binary @"C:\Vault\Object Records\create_object_records.csv" \
https://myvault.veevavault.com/api/v24.3/vobjects/product__v
```

## Response

```json
{
    "responseStatus": "SUCCESS",
    "data": [
        {
            "responseStatus": "SUCCESS",
            "data": {
                "id": "0PR0771",
                "url": "api/v8.0/vobjects/product__v/0PR0771"
            }
        },
        {
            "responseStatus": "SUCCESS",
            "data": {
                "id": "0PR0772",
                "url": "api/v8.0/vobjects/product__v/0PR0772"
            }
        },
        {
            "responseStatus": "SUCCESS",
            "data": {
                "id": "0PR0773",
                "url": "api/v8.0/vobjects/product__v/0PR0773"
            }
        },
        {
            "responseStatus": "FAILURE",
            "errors": [
                {
                    "type": "INVALID_DATA",
                    "message": "Error message describing why this object record was not created."
                }
            ]
        }
    ]
}
```

## Endpoint Details

`POST /api/{version}/vobjects/{object_name}`

### Important Notes

- Maximum input file size is 50 MB
- Values in the input must be UTF-8 encoded
- CSVs must follow the standard RFC 4180 format, with some exceptions
- Vault removes XML characters that fall outside of the character range from the request body
- Maximum batch size is 500
- You can only add relationships on object fields using ID values or based on a unique field on the target object
- This API does not support object lookup fields

### Headers

| Name | Description |
|------|-------------|
| Content-Type | text/csv or application/json |
| Accept | application/json (default) or text/csv |
| X-VaultAPI-MigrationMode | If true, allows creating/updating records in noninitial state with minimal validation. Requires Record Migration permission. |
| X-VaultAPI-NoTriggers | If true and Record Migration Mode enabled, bypasses all standard and custom SDK triggers. |

### URI Path Parameters

| Name | Description |
|------|-------------|
| {object_name} | The name of the object, for example, product__v |

### Body Parameters

Upload parameters as a JSON or CSV file. The following shows the required standard fields, but an Admin may set other standard or custom object fields as required in your Vault.

> Note: If an object has a field default configured, the value you use for that field overrides the default.

| Name | Description |
|------|-------------|
| name__v | **Required** unless system-managed. Check the name__v field's system_managed_name property. |
| object_type__v | **Optional**. The id of the object type. Cannot be used with object_type__v.api_name__v. |
| object_type__v.api_name__v | **Optional**. The name of the object type. Cannot be used with object_type__v. |
| source_record_id | **Optional**. ID of existing record to copy. Other field values override copied values. |
| {field_name} | **Optional**. Any object field that is editable (editable: true). |
| state__v | **Optional**. Lifecycle state of record when Migration Mode enabled. Example: draft_state__c. |
| state_label | **Optional**. Lifecycle state type in Migration Mode. Format: base:object_lifecycle:{type}. |

## Add Relationships on Object Fields

Many object records have relationships with other object records. For example, the Marketing Campaign "CholeCap Campaign" references its parent "CholeCap" Product record. 

When creating or upserting object records:

- Object fields in your input file can indicate relationships
- Supports reference relationships and parent-child relationships within fields
- Does not support lookup fields
- To refer to relationships, combine relationship name with unique field (e.g. name__v)
- Example: product__vr.name__v references the name of the related Product record

## Create Link Target Records

In PromoMats Vaults, use this to create Claim (annotation_keywords__sys) records with valid references to anchor annotations (annotation_types=anchor__sys).

The Link Target (link_target__sys) object:
- Establishes relationships to documents, anchors, and permalinks
- Not visible by default to users in the UI
- API allows creating records referencing anchor annotations
- Provide annotation ID and document version ID
- Vault auto-populates anchor-related fields:
  - Anchor Id (anchor_id__sys)
  - Anchor Title (anchor_title__sys)
  - Anchor Page (anchor_page__sys)
  - Reference (target__sys)

### Body Parameters for Link Target Records

| Name | Description |
|------|-------------|
| annotation_id__sys | **Required**. The annotation's ID from Read Annotations API. |
| suggestedlink_link_target_type__v | **Required**. The suggested link target type (e.g. anchor__v). |
| document_version_id__v | **Required**. Document ID and version in format {id}_{major}_{minor}. |

## Add Attachment Fields

To specify a value for an Attachment field:
- Provide the file path on the file staging server
- Maximum allowed file size is 100 MB

## Upsert Object Records

Upsert combines create and update operations:
- Use idParam to identify records by any unique field
- One input file can create new records and update existing ones
- Matching records are updated with specified values
- Non-matching records are created new
- Expects unique idParam values (duplicates cause FAILURE)
- To set/change object type, include object_type__v and use Migration Mode
- Without Migration Mode, updates with object_type__v fail unless matching existing value

### Query String Parameters

| Name | Description |
|------|-------------|
| idParam | Field name to identify records for upsert. Must be unique. Example: idParam=external_id__v |

## Create User Object Records

To create user__sys records:

### Required Fields and Notes
- Must include all required user__sys fields
- Can create users in pending state by setting future activation_date__sys
- Can defer welcome emails
- Get full field list from Object Metadata API on user__sys

### Limitations
- Cannot create cross-domain users (use Create Single User endpoint)
- Cannot add domain-only users (use Create Single User endpoint)
- Cannot add VeevaID users (use Create Single User endpoint)
- Cannot change user passwords

### Body Parameters

| Name | Description |
|------|-------------|
| email__sys | **Required**. User's email address. Prevents duplicate users. |
| first_name__sys | **Required**. User's first name. |
| last_name__sys | **Required**. User's last name. |
| username__sys | **Required**. Full Vault username (login). |
| language__sys | **Required**. User's preferred language. |
| locale__sys | **Required**. User's location. |
| timezone__sys | **Required**. User's time zone. |
| license_type__sys | **Optional**. License type, defaults to full__v. |
| security_profile__sys | **Required**. User's security profile. |
| status__v | **Optional**. User status. |
| source_person_id__v | **Optional**. Associated person record (Clinical Ops only). |
| activation_date__sys | **Optional**. First access date (YYYY-MM-DD). Defaults to today. |
| send_welcome_email__sys | **Optional**. Defer welcome email until activation (true) or never send (false). |
| layout_profile__sys | **Optional**. ID of layout profile to assign. |

> Note: Changes to user__sys sync across all Vaults where that user is a member, including cross-domain Vaults.

## Response Details

Vault returns a responseStatus for the request:

- **SUCCESS**: This request executed with no warnings. Individual records may be failures.
- **WARNING**: When upserting records, this request executed with at least one warning on an individual record. Other individual records may be failures.
- **FAILURE**: This request failed to execute. For example, an invalid sessionId.

On SUCCESS or WARNING, Vault returns a responseStatus for each individual record in the same order provided in the input. The responseStatus for each record can be one of the following:

- **SUCCESS**: Vault successfully updated at least one field value on this record.
- **WARNING**: When upserting records, Vault successfully evaluated this record and reported a warning. For example, Vault returns a warning for records that process with no changes (no-op).
- **FAILURE**: This record could not be evaluated and Vault made no field value changes. For example, an invalid or duplicate record ID.

Note that in CTMS Vaults, if you do not specify a milestone record ID when creating a new Monitoring Event record, this call will automatically create a new Milestone record. However, the id of the new Milestone record is not returned in this response. Learn more about automated CTMS object creation in Vault Help.