# Object Types

Vault Objects can be partitioned into Object Types. For example, a Product object may have two different object types: "Pharmaceutical Product" and "Medical Device Product". These object types may share some fields but also have fields only used in each object type. By using object types, two product groups can not only manage data specific to their business but also easily report on products in both groups.

## Retrieve Details from All Object Types

### Request

```bash
curl -X GET -H "Authorization: {SESSION_ID}" \
    https://myvault.veevavault.com/api/v24.3/configuration/Objecttype
```

Retrieve all object types and object type fields in the authenticated Vault.

`GET /api/{version}/configuration/Objecttype`

### Headers

| Name | Description |
|------|-------------|
| Accept | application/json (default) or application/xml |

The response lists all object types and all fields configured on each object type. See the next response for details.

## Retrieve Details from a Specific Object

### Request

```bash
curl -X GET -H "Authorization: {SESSION_ID}" \
    https://myvault.veevavault.com/api/v24.3/configuration/Objecttype.bicycle__c.road_bike__c?loc=true
```

### Response

```json
{
   "responseStatus": "SUCCESS",
   "data": {
       "localized_data": {
           "label_plural": {
               "en": "Road Bikes",
               "fr": "Vélos de route",
               "es": "Bicicletas de carretera"
           },
           "label": {
               "en": "Road Bike",
               "fr": "Vélo de route",
               "es": "Bicicleta de carretera"
           }
       },
       "name": "road_bike__c",
       "object": "bicycle__c",
       "active": true,
       "description": "This object type is intended for model numbers 400-650. For model numbers 650-900, use the Hybrid Bike object type.",
       "additional_type_validations": [],
       "label_plural": "Road Bikes",
       "type_fields": [
           {
               "required": false,
               "name": "id",
               "source": "standard"
           },
           {
               "required": false,
               "name": "object_type__v",
               "source": "standard"
           },
           {
               "required": false,
               "name": "global_id__sys",
               "source": "system"
           },
           {
               "required": false,
               "name": "link__sys",
               "source": "system"
           },
           {
               "required": true,
               "name": "name__v",
               "source": "standard"
           },
           {
               "required": true,
               "name": "status__v",
               "source": "standard"
           },
           {
               "required": false,
               "name": "created_by__v",
               "source": "standard"
           },
           {
               "required": false,
               "name": "created_date__v",
               "source": "standard"
           },
           {
               "required": false,
               "name": "modified_by__v",
               "source": "standard"
           },
           {
               "required": false,
               "name": "modified_date__v",
               "source": "standard"
           }
       ],
       "label": "Road Bike"
   }
}
```

Retrieve all object types and object type fields configured on a given object.

`GET /api/{version}/configuration/{object_name_and_object_type}`

### Headers

| Name | Description |
|------|-------------|
| Accept | application/json (default) or application/xml |

### URI Path Parameters

| Name | Description |
|------|-------------|
| {object_name_and_object_type} | The object name followed by the object type in the format Objecttype.{object_name}.{object_type}. For example, Objecttype.product__v.base__v |

### Query Parameters

| Name | Description |
|------|-------------|
| loc | When localized (translated) strings are available, retrieve them by setting loc to true |

The response lists all object types and all fields configured on each object type for the specific object.

## Change Object Type

### Request

```bash
curl -X POST -H "Authorization: {SESSION_ID}" \
    -H "Content-Type: text/csv" \
    -H "Accept: application/json" \
    --data-binary @"C:\Vault\Objects\objecttypes.csv" \
    https://myvault.veevavault.com/api/v24.3/vobjects/product__v/actions/changetype
```

### Response

```json
{
    "responseStatus": "SUCCESS",
    "data": [
        {
            "responseStatus": "SUCCESS",
            "data": {
                "id": "00P07710",
                "url": "api/v24.2/vobjects/product__v/00P07710"
            }
        }
    ]
}
```

Change the object types assigned to object records. Any field values that exist on both the original and new object type will carry over to the new type. All other field values will be removed, as only fields on the new type are valid. You can set field values on the new object type in the CSV input.

- The maximum input file size is 1GB
- The values in the input must be UTF-8 encoded
- CSVs must follow the standard format
- The maximum batch size is 500

`POST /api/{version}/vobjects/{object_name}/actions/changetype`

### Headers

| Name | Description |
|------|-------------|
| Content-Type | application/json or text/csv |
| Accept | application/json (default) or text/csv |

### URI Path Parameters

| Name | Description |
|------|-------------|
| {object_name} | The name of the object |

### Body Parameters

Upload parameters as a JSON or CSV file.

| Name | Description |
|------|-------------|
| id (required) | The ID of the object record |
| object_type__v (required) | The ID of the new object type |
