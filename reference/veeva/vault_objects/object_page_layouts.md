# Object Page Layouts

Object page layouts are defined at the object or object-type level and control the information displayed to a user on the object record detail page. Objects that include multiple object types can define a different layout for each type. Learn more about configuring object page layouts in Vault Help.

The page layout APIs consider the authenticated user's permissions, so fields which are hidden from the authenticated user will not be included in the API response. For example, field-level security, object controls, and other object-level permissions are considered. Record-level permissions such as atomic security are not considered. Layout rules are not applied, but instead have their configurations returned as metadata. Both active and inactive fields are included in the response.

## Retrieve Page Layouts

### Request

```bash
curl -X GET -H "Authorization: {SESSION_ID}" \
https://myvault.veevavault.com/api/v24.3/metadata/vobjects/product__v/page_layouts
```

### Response

```json
{
   "responseStatus": "SUCCESS",
   "data": [
       {
           "name": "product_detail_page_layout__c",
           "label": "Product Detail Page Layout",
           "object_type": "base__v",
           "url": "/api/v24.3/metadata/vobjects/product__v/page_layouts/product_detail_page_layout__c",
           "active": true,
           "description": "General layout for any product",
           "default_layout": true,
           "display_lifecycle_stages": false
       },
       {
           "name": "otc_product_layout__c",
           "label": "OTC Product Layout",
           "object_type": "base__v",
           "url": "/api/v24.3/metadata/vobjects/product__v/page_layouts/otc_product_layout__c",
           "active": true,
           "description": "New layout for OTC products",
           "default_layout": false,
           "display_lifecycle_stages": false
       },
       {
           "name": "generic_product_layout__c",
           "label": "Generic Product Layout",
           "object_type": "base__v",
           "url": "/api/v24.3/metadata/vobjects/product__v/page_layouts/generic_product_layout__c",
           "active": true,
           "description": "Layout for generics",
           "default_layout": false,
           "display_lifecycle_stages": false
       }
   ]
}
```

### Endpoint Details

`GET /api/{version}/metadata/vobjects/{object_name}/page_layouts`

#### Headers

| Name | Description |
|------|-------------|
| Accept | application/json (default) or application/xml |

#### URI Path Parameters

| Name | Description |
|------|-------------|
| {object_name} | The name of the object from which to retrieve page layouts. |

### Response Details

On SUCCESS, the response lists all layouts associated with the specified object. Each layout includes:

| Name | Description |
|------|-------------|
| name | The name of the layout. |
| label | The label of the layout as it appears in the Vault UI. |
| object_type | The object type where the layout is available. |
| active | The active or inactive status of the layout. |
| description | A description of the layout. |
| default_layout | If true, this layout is assigned to all users unless another layout is specified in their assigned Layout Profile. |
| display_lifecycle_stages | For objects with lifecycle stages configured, if true, Vault displays the Lifecycle Stages Chevron panel on all views for the object. |

## Retrieve Page Layout Metadata

### Request

```bash
curl -X GET -H "Authorization: {SESSION_ID}" \
https://myvault.veevavault.com/api/v24.3/metadata/vobjects/my_object__c/page_layouts/my_object_detail_page_layout__c
```

### Response

```json
{
    "responseStatus": "SUCCESS",
    "data": {
        "name": "my_object_detail_page_layout__c",
        "label": "My Object Detail Page Layout",
        "object": "my_object__c",
        "object_type": "base__v",
        "active": true,
        "description": "",
        "default_layout": true,
        "display_lifecycle_stages": false,
        "created_date": "2023-12-04T21:11:32.000Z",
        "last_modified_date": "2023-12-04T23:44:56.000Z",
        "layout_rules": [
            {
                "evaluation_order": 100,
                "status": "active__v",
                "fields_to_hide": [],
                "sections_to_hide": [
                    "my_related_objects__c"
                ],
                "controls_to_hide": [],
                "hide_layout": false,
                "hidden_pages": [],
                "displayed_as_readonly_fields": [
                    "link__sys"
                ],
                "displayed_as_required_fields": [
                    "my_related_object__c"
                ],
                "focus_on_layout": true,
                "expression": "IsBlank(my_related_object__c)"
            }
        ],
        "sections": [
            {
                "name": "details__c",
                "title": "Details",
                "type": "detail",
                "help_content": null,
                "show_in_lifecycle_states": [],
                "properties": {
                    "layout_type": "One-Column",
                    "items": [
                        {
                            "type": "field",
                            "status": "active__v"
                        }
                    ]
                }
            },
            {
                "name": "my_related_objects__c",
                "title": "My Related Objects",
                "type": "related_object",
                "help_content": null,
                "show_in_lifecycle_states": [],
                "properties": {
                    "relationship": "my_related_objects__cr",
                    "related_object": "my_related_object__c",
                    "prevent_record_create": false,
                    "modal_create_record": false,
                    "criteria_vql": null,
                    "columns": []
                }
            }
        ]
    }
}
```

### Endpoint Details

`GET /api/{version}/metadata/vobjects/{object_name}/page_layouts/{layout_name}`

#### Headers

| Name | Description |
|------|-------------|
| Accept | application/json (default) or application/xml |

#### URI Path Parameters

| Name | Description |
|------|-------------|
| {object_name} | The name of the object from which to retrieve page layout metadata. |
| {layout_name} | The name of the page layout from which to retrieve metadata. |

### Response Details

On SUCCESS, returns metadata for the specified page layout, including the object_type, layout_rules, and sections. The response considers user permissions but includes both active and inactive fields. Layout rules are returned as metadata rather than being applied.