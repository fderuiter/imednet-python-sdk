# Retrieve Object Record

## Request

```bash
curl -X GET -H "Authorization: {SESSION_ID}" \
https://myvault.veevavault.com/api/v24.3/vobjects/product__v/0PR0202
```

## Response

```json
{
  "responseStatus": "SUCCESS",
  "responseDetails": {
    "url": "/api/v24.3/vobjects/product__v/00PR0202",
    "object": {
      "url": "/api/v24.3/metadata/vobjects/product__v",
      "label": "Product",
      "name": "product__v",
      "label_plural": "Products",
      "prefix": "00P"
    }
  },
  "data": {
    "external_id__v": "CHO-457",
    "product_family__c": [
      "cholepriol__c"
    ],
    "compound_id__c": "CHO-55214",
    "abbreviation__c": "CHO",
    "therapeutic_area__c": [
      "endocrinology__c"
    ],
    "name__v": "CholeCap",
    "modified_by__v": 12022,
    "modified_date__v": "2016-05-10T21:06:11.000Z",
    "inn__c": null,
    "created_date__v": "2015-07-30T20:55:16.000Z",
    "id": "00PR0202",
    "internal_name__c": null,
    "generic_name__c": "cholepridol phosphate",
    "status__v": [
      "active__v"
    ],
    "created_by__v": 1
  },
  "manually_assigned_sharing_roles": {
    "owner__v": {
      "groups": null,
      "users": [
        12022
      ]
    },
    "viewer__v": {
      "groups": [
        3311303
      ],
      "users": [
        35551,
        48948,
        55002
      ]
    },
    "editor__v": {
      "groups": [
        4411606
      ],
      "users": [
        60145,
        70012,
        89546
      ]
    }
  }
}
```

**Endpoint:** `GET /api/{version}/vobjects/{object_name}/{object_record_id}`

## Headers

| Name | Description |
| ---- | ----------- |
| Accept | application/json (default) or application/xml |

## URI Path Parameters

| Name | Description |
| ---- | ----------- |
| {object_name} | The object name__v field value (product__v, country__v, custom_object__c, etc.). |
| {object_record_id} | The object record id field value. |

## Response Details

On SUCCESS, the response lists all fields and values configured on the object record.

When Custom Sharing Rules have been enabled on the object (`"dynamic_security": true`), the response includes the following additional information:

- **manually_assigned_sharing_roles**
  - owner__v
  - viewer__v
  - editor__v

These are the users and groups that have been manually assigned to each role on the object record.

> **Note**: Not all object records will have users and groups assigned to roles. You can update object records to add or remove users and/or groups on each role.
