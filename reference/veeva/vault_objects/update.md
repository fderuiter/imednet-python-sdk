# Update Object Records

## Request

```bash
curl -X PUT -H "Authorization: {SESSION_ID}" \
-H "Content-Type: text/csv" \
-H "Accept: text/csv" \
--data-raw 'id,generic_name__vs,product_family__vs,abbreviation__vs,therapeutic_area__vs,manufacturer_name__v,regions__c
00P000000000602,Gluphosphate,gluphosphate__c,GLU,cardiology__vs,Veeva Labs,north_america__c
00P00000000K001,nitroprinaline__c,,NYA,veterinary__c,Veeva Labs,europe__c
00P00000000Q007,veniladrine sulfate,"veniladrine__c,vendolepene__c",VPR,psychiatry__vs,Veeva Labs,"north_america__c,south_america__c"' \
https://myvault.veevavault.com/api/v24.3/vobjects/product__v
```

## Response

```json
{
   "responseStatus": "WARNING",
   "warnings": [
       {
           "warning_type": "NO_DATA_CHANGES",
           "message": "No changes in values - one or more records not updated"
       }
   ],
   "data": [
       {
           "responseStatus": "SUCCESS",
           "data": {
               "id": "00P000000000602",
               "url": "/api/v24.3/vobjects/product__v/00P000000000602"
           }
       },
       {
           "responseStatus": "WARNING",
           "warnings": [
               {
                   "warning_type": "NO_DATA_CHANGES",
                   "message": "No changes in values - record not updated"
               }
           ],
           "data": {
               "id": "00P00000000K001",
               "url": "/api/v24.3/vobjects/product__v/00P00000000K001"
           }
       },
       {
           "responseStatus": "FAILURE",
           "errors": [
               {
                   "type": "INVALID_DATA",
                   "message": "The resource [00P00000000Q007] does not exist"
               }
           ]
       }
   ]
}
```

Update Object Records in bulk. You can use this endpoint to update user records (user__sys).

### Important Notes
- The maximum input size is 50 MB
- The values in the input must be UTF-8 encoded
- CSVs must follow the standard RFC 4180 format, with some exceptions
- Vault removes XML characters that fall outside of the character range from the request body
- The maximum batch size is 500

### Endpoint
`PUT /api/{version}/vobjects/{object_name}`

### Headers

| Name | Description |
|------|-------------|
| Content-Type | text/csv or application/json |
| Accept | application/json (default) or text/csv |
| X-VaultAPI-MigrationMode | If set to true, Vault allows you to update object records in a noninitial state and with minimal validation, create inactive records, and set standard and system-managed fields such as created_by__v. Does not bypass record triggers. Use the X-VaultAPI-NoTriggers header to bypass all standard and custom SDK triggers. You must have the Record Migration permission to use this header. |
| X-VaultAPI-NoTriggers | If set to true and Record Migration Mode is enabled, it bypasses all standard and custom SDK triggers. |

### URI Path Parameters

| Name | Description |
|------|-------------|
| {object_name} | The name of the object, for example, product__v |

### Body Parameters
Include parameters as JSON or CSV. The following shows the required standard fields, but an Admin may set other standard or custom object fields as required in your Vault.

| Name | Description |
|------|-------------|
| id (required) | The object record ID. You can only update an object record ID once per request. If you provide duplicate IDs, the bulk update fails any duplicate records. Instead of id, you can use a unique field defined by the idParam query parameter. |
| {field_name} (optional) | The field name to update on this object record. Use the Object Metadata API to retrieve all fields configured on objects. You can update any field with editable: true. |
| state__v (optional) | Specifies the lifecycle state of the record when X-VaultAPI-MigrationMode is set to true. For example, draft_state__c. |
| state_label (optional) | Specifies the lifecycle state type of the record when X-VaultAPI-MigrationMode is set to true. Use the format base:object_lifecycle: followed by the object state type. |

### Updating Attachment Fields
To update an Attachment field type, provide the file path on the file staging server. You can also use Update Attachment Field File to update a single Attachment field for an existing record.

- The maximum allowed file size for Attachment fields is 100 MB
- To make no changes to the field, provide the existing attachment's file handle
- To clear the field, leave the value blank

### Query Parameters

| Name | Description |
|------|-------------|
| idParam | Optional: To identify objects in your input by a unique field, add idParam={field_name} to the request endpoint. You can use any object field that has unique set to true in the object metadata. For example, idParam=external_id__v. |

### Additional Notes

- If an object is a parent in a parent-child relationship with another object, you cannot update its status__v field in bulk
- If an object has a field default configured, the value you use for that field overrides the default
- If Dynamic Security (Custom Sharing Rules) is configured on an object, you can add or remove users and groups on manually assigned roles
- You can also use this call to complete user tasks by setting the complete__v field to true
- The Edit permission is required on the object record when updating role assignments
- When you create, add, or update user__sys, Vault synchronizes those changes with users across all Vaults to which that user is a member
- You can use this endpoint to update checkbox fields to a null value

### Response Details
Vault returns a responseStatus for the request:

- **SUCCESS**: This request executed with no warnings. Individual records may be failures
- **WARNING**: This request executed with at least one warning on an individual record. Other individual records may be failures
- **FAILURE**: This request failed to execute. For example, an invalid sessionId

On SUCCESS or WARNING, Vault returns a responseStatus for each individual record in the same order provided in the input. The responseStatus for each record can be one of the following:

- **SUCCESS**: Vault successfully updated at least one field value on this record
- **WARNING**: Vault successfully evaluated this record and reported a warning
- **FAILURE**: This record could not be evaluated and Vault made no field value changes

### About No-Ops
An API call which causes no operation to occur is called a no-op. For example, a call to update values on an object record which already has all of the requested values. The call succeeds and no operation occurs.

When the API processes a record with no changes, Vault:
- Does not update the record's last_modified_date
- Does not create an entry in the object record audit history
- Does not execute SDK triggers