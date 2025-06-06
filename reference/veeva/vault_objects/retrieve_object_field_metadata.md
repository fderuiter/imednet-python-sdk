## Retrieve Object Field Metadata

### Request

```bash
curl -X GET -H "Authorization: {SESSION_ID}" \
https://myvault.veevavault.com/api/v24.3/metadata/vobjects/product__v/fields/name__v
```

### Response

```json
{
    "responseStatus": "SUCCESS",
    "field": {
        "lookup_relationship_name": null,
        "description": "Do not remove from layout.",
        "start_number": null,
        "source": "standard",
        "type": "String",
        "required": true,
        "list_column": true,
        "facetable": false,
        "format_mask": null,
        "max_length": 128,
        "order": 1,
        "help_content": "The primary name of the product as you wish to see it referenced throughout the system; this may be a brand name or a generic name, but will be visible globally.",
        "editable": true,
        "label": "Product Name",
        "modified_date": "2024-05-15T21:20:44.000Z",
        "created_by": 1,
        "no_copy": false,
        "encrypted": false,
        "system_managed_name": false,
        "value_format": null,
        "unique": true,
        "name": "name__v",
        "modified_by": 133999,
        "created_date": "2023-01-20T19:05:46.000Z",
        "sequential_naming": false,
        "lookup_source_field": null,
        "status": [
            "active__v"
        ]
    }
}
```

**Endpoint:** `GET /api/{version}/metadata/vobjects/{object_name}/fields/{object_field_name}`

### Headers

| Name | Description |
| ---- | ----------- |
| Accept | application/json (default) or application/xml |

### URI Path Parameters

| Name | Description |
| ---- | ----------- |
| {object_name} | The object name__v field value (product__v, country__v, custom_object__c, etc.). |
| {object_field_name} | The object field name value (id, name__v, external_id__v, etc.). |

### Query Parameters

| Name | Description |
| ---- | ----------- |
| loc | Set to true to retrieve the localized_data array, which contains the localized (translated) strings for the label and label_plural object fields. If omitted, defaults to false and localized Strings are not included. |

### Response Details

The response lists all metadata configured on the specified Vault object field. Note the following field metadata:

| Metadata Field | Description |
| -------------- | ----------- |
| required | When true, the field value must be set when creating new object records. |
| editable | When true, the field value can be defined by the currently authenticated user. When false, the field value is read-only or system-managed. |
| no_copy | When true, field values are not copied when using the Make a Copy action. |
| facetable | When true, the field is available for use as a faceted filter in the Vault UI. Learn more about faceted filters in Vault Help. |
| searchable | Boolean indicating the lookup field is searchable. When true, the field is available for filtering and ordering with VQL and in the Vault UI. Only applies to lookup fields. Learn more about lookup fields on Vault Help. |
| format_mask | The format mask expression if it exists on the field. Learn more about format masks in Vault Help. |
