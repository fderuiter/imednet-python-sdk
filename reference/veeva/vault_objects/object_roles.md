# Object Roles

Object records can have different roles available to them depending on their type and lifecycles. There are a set of standard roles that ship with Vault: owner__v, viewer__v, and editor__v. In addition, Admins can create custom roles defined per lifecycle. Not all object records will have users and groups assigned to roles.

Learn more about roles on object records in Vault Help.

Through the object record role APIs, you can:
- Retrieve available roles on object records
- Retrieve who is currently assigned to a role
- Add additional users and groups to a role
- Remove users and groups from roles

Note that all user and group information is returned as IDs, so you need to use the Retrieve User or Retrieve Group API to determine the name.

For roles on documents or binders, see Roles.

## Retrieve Object Record Roles

### Request

```bash
curl -X GET -H "Authorization: {SESSION_ID}" \
    https://myvault.veevavault.com/api/v24.3/vobjects/campaign__c/OBE000000000412/roles
```

### Response

```json
{
    "responseStatus": "SUCCESS",
    "data": [
        {
            "name": "approver__c",
            "users": [
                61583,
                61584,
                86488
            ],
            "groups": [
                3,
                1392631750101
            ],
            "assignment_type": "manual_assignment"
        }
    ]
}
```

Retrieve manually assigned roles on an object record and the users and groups assigned to them.

`GET /api/{version}/vobjects/{object_name}/{id}/roles{/role_name}`

### Headers

| Name | Description |
|------|-------------|
| Accept | application/json (default) or application/xml |

### URI Path Parameters

| Name | Description |
|------|-------------|
| {object_name} | The object name |
| {id} | The id of the document, binder, or object record |
| {/role_name} | Optional: Include a role name to filter for a specific role. For example, owner__v |

### Response Details

Even though the owner__v role is automatically assigned when you apply Custom Sharing Rules, the assignment_type for roles on objects is always manual_assignment.

## Assign Users & Groups to Roles on Object Records

### Request

```bash
curl -X POST -H "Authorization: {SESSION_ID}" \
    -H "Content-Type: text/csv" \
    -H "Accept: text/csv" \
    --data-binary @"C:\Vault\Roles\assign_object_record_roles.csv" \
    https://myvault.veevavault.com/api/v24.3/vobjects/campaign__c/roles
```

### Response

```json
{
    "responseStatus": "SUCCESS",
    "data": [
        {
            "responseStatus": "SUCCESS",
            "data": {
                "id": "OBE000000000412"
            }
        }
    ]
}
```

### Example JSON Request Body

```json
[
  {
    "id": "OBE000000000412",
    "roles": [
      {
        "role": "content_creator__c",
        "users": "61590"
      }
    ]
  }
]
```

Assign users and groups to roles on an object record in bulk.

- The maximum CSV input file size is 1GB
- The values in the input must be UTF-8 encoded
- CSVs must follow the standard RFC 4180 format
- The maximum batch size is 500

Assigning users and groups to roles is additive, and duplicate groups are ignored. For example, if groups 1 and 2 are currently assigned to a particular role and you assign groups 2 and 3 to the same role, the final list of groups assigned to the role will be 1, 2, and 3.

`POST /api/{version}/vobjects/{object_name}/roles`

### Headers

| Name | Description |
|------|-------------|
| Content-Type | text/csv or application/json |
| Accept | application/json (default), text/csv, or application/xml |

### URI Path Parameters

| Name | Description |
|------|-------------|
| {object_name} | The name of the object where you want to update records |

### Body Parameters

Prepare a JSON or CSV input file. User and group assignments are ignored if they are invalid, inactive, or already exist.

| Name | Description |
|------|-------------|
| id (required) | The object record ID |
| role__v.users (optional) | A string of user id values for the new role |
| role__v.groups (optional) | A string of group id values for the new role |

### Response Details

On SUCCESS, The response includes the object record id.

## Remove Users & Groups from Roles on Object Records

### Request

```bash
curl -X POST -H "Authorization: {SESSION_ID}" \
    -H "Content-Type: text/csv" \
    -H "Accept: text/csv" \
    --data-binary @"C:\Vault\Roles\remove_object_record_roles.csv" \
    https://myvault.veevavault.com/api/v24.3/vobjects/campaign__c/roles
```

### Response

```json
{
    "responseStatus": "SUCCESS",
    "data": [
        {
            "responseStatus": "SUCCESS",
            "data": {
                "id": "OBE000000000412"
            }
        }
    ]
}
```

### Example JSON Request Body

```json
[
  {
    "id": "OBE000000000412",
    "roles": [
      {
        "role": "content_creator__c",
        "users": "61590"
      }
    ]
  }
]
```

Remove users and groups from roles on an object record in bulk.

- The maximum CSV input file size is 1GB
- The values in the input must be UTF-8 encoded
- CSVs must follow the standard RFC 4180 format
- The maximum batch size is 500

`DELETE /api/{version}/vobjects/{object_name}/roles`

### Headers

| Name | Description |
|------|-------------|
| Content-Type | text/csv or application/json |
| Accept | application/json (default), text/csv, or application/xml |

### URI Path Parameters

| Name | Description |
|------|-------------|
| {object_name} | The name of the object where you want to remove roles |

### Body Parameters

Prepare a JSON or CSV input file. Users and groups are ignored if they are invalid or inactive.

| Name | Description |
|------|-------------|
| id (required) | The object record ID |
| role__v.users (optional) | A string of user id values to remove |
| role__v.groups (optional) | A string of group id values to remove |

## Object Record Attachments

### Determine if Attachments are Enabled on an Object

### Request

```bash
curl -X GET -H "Authorization: {SESSION_ID}" \
    https://myvault.veevavault.com/api/v24.3/metadata/vobjects/site__v
```

### Response

```json
{
    "responseStatus": "SUCCESS",
    "object": {
        "created_date": "2014-02-03T20:12:29.000Z",
        "created_by": 1,
        "allow_attachments": true,
        "auditable": true,
        "modified_date": "2015-01-06T22:34:15.000Z",
        "status": [
            "active__v"
        ],
        "urls": {
            "field": "/api/v24.3/metadata/vobjects/site__v/fields/{NAME}",
            "record": "/api/v24.3/vobjects/site__v/{id}",
            "attachments": "/api/v24.3/vobjects/site__v/{id}/attachments",
            "list": "/api/v24.3/vobjects/site__v",
            "metadata": "/api/v24.3/metadata/vobjects/site__v"
        },
        "label_plural": "Study Sites",
        "role_overrides": false,
        "label": "Study Site",
        "in_menu": true,
        "help_content": null,
        "source": "standard",
        "order": null,
        "modified_by": 46916,
        "description": null,
        "name": "site__v"
    }
}
```

`GET /api/{version}/metadata/vobjects/{object_name}`

### Headers

| Name | Description |
|------|-------------|
| Accept | application/json (default) or application/xml |

### URI Path Parameters

| Name | Description |
|------|-------------|
| {object_name} | The object name__v field value (product__v, country__v, custom_object__c, etc.) |

### Response Details

Shown above, “allow_attachments” is set to true for this object and “attachments” is included in the list of urls, indicating that attachments are enabled on the site__v object. This means that any of the object records can have attachments.

