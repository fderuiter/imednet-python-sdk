# Picklists

Picklists allow users to select a value for a field from a range of predefined options. A single picklist may contain up to 2,000 options (values). The API supports retrieving picklists and picklist values, creating and deleting picklist values, and updating picklist value labels and names. The API does not support creating, updating, or deleting the picklists themselves; this must be done in the Admin UI.

Learn about managing picklists in Vault Help.

## Retrieve All Picklists

### Request

```bash
curl -X GET -H "Authorization: {SESSION_ID}" \
    https://myvault.veevavault.com/api/v24.3/objects/picklists
```

### Response

```json
{
  "responseStatus": "SUCCESS",
  "responseMessage": "Success",
  "errorCodes": null,
  "picklists": [
    {
      "name": "asset_type__c",
      "label": "Asset Type",
      "kind": "global",
      "usedIn": [
        {
          "documentTypeName": "promotional_piece__c:advertisement__c:web__c",
          "propertyName": "assetType_pm"
        },
        {
          "documentTypeName": "claim__c",
          "propertyName": "assetType_pm"
        }
      ]
    },
    {
      "name": "audience__c",
      "label": "Audience",
      "kind": "global",
      "usedIn": [
        {
          "documentTypeName": "promotional_piece__c",
          "propertyName": "audience_pm"
        }
      ]
    },
    {
      "name": "branding__c",
      "label": "Branding",
      "kind": "global",
      "usedIn": [
        {
          "documentTypeName": "promotional_piece__c",
          "propertyName": "brandingStatus_pm"
        }
      ]
    },
    {
      "name": "campaign_name__c",
      "label": "Campaign",
      "kind": "global",
      "usedIn": [
        {
          "documentTypeName": "promotional_piece__c",
          "propertyName": "campaign_pm"
        }
      ]
    },
    {
      "name": "claim_category__c",
      "label": "Claim Category",
      "kind": "global",
      "usedIn": [
        {
          "documentTypeName": "claim__c",
          "propertyName": "claimCategory_pm"
        }
      ]
    },
    {
      "name": "email_template_type__v",
      "label": "Email Template Type",
      "kind": "global",
      "system": true,
      "usedIn": [
        {
          "documentTypeName": "email_template__v",
          "propertyName": "emailTemplateType_b"
        }
      ]
    },
    {
      "name": "language__v",
      "label": "Language",
      "kind": "global",
      "system": true,
      "usedIn": [
        {
          "documentTypeName": "base_document__v",
          "propertyName": "language__v"
        }
      ]
    }
  ],
  "errorType": null
}
```

### Headers

| Name | Description |
|------|-------------|
| Accept | application/json (default) or application/xml |

### Response Details

| Metadata Field | Description |
|----------------|-------------|
| name | Picklist name. This is used only in the API and displayed in the Admin UI. |
| label | Picklist label. This is used in the API and UI. Users see the label on document and object picklist fields. |
| kind | There are two kinds of picklists: global picklists apply to documents and objects; user picklists apply to Vault users. |
| system | Indicates if the picklist is system-managed. If true, the picklist values cannot be added, edited, or removed. |
| usedIn | The document type or object in which the picklist is defined. |
| documentTypeName | For document picklists, this the document type name in which the picklist is defined. |
| objectName | For object picklists, this is the object name in which the picklist is defined. |
| propertyName | For document picklists, this is the document field name using the picklist. For object picklists, this is the object field name using the picklist. |

## Retrieve Picklist Values

### Request

```bash
curl -X GET -H "Authorization: {SESSION_ID}" \
    https://myvault.veevavault.com/api/v24.3/objects/picklists/license_type__v
```

### Response

```json
{
  "responseStatus": "SUCCESS",
  "responseMessage": "Success",
  "picklistValues": [
    {
      "name": "full__v",
      "label": "Full User"
    },
    {
      "name": "read_only__v",
      "label": "Read-only User"
    },
    {
      "name": "external__v",
      "label": "External User"
    },
    {
      "name": "view_based__v",
      "label": "View-Based User"
    }
  ]
}
```

### Headers

| Name | Description |
|------|-------------|
| Accept | application/json (default) or application/xml |

### URI Path Parameters

| Name | Description |
|------|-------------|
| {picklist_name} | The picklist name field value (license_type__v, product_family__c, region__c, etc.) |

### Response Details

| Name | Description |
|------|-------------|
| name | The picklist value name. This is used only in the API and displayed in the Admin UI. |
| label | The picklist value label. This is used in the API and UI. Users see the label when selecting picklist values. |

## Create Picklist Values

### Request

```bash
curl -X POST -H "Authorization: {SESSION_ID}" \
    -H "Content-Type: application/x-www-form-urlencoded" \
    -d "value_1=North America" \
    -d "value_2=Central America" \
    -d "value_3=South America" \
    https://myvault.veevavault.com/api/v24.3/objects/picklists/regions__c
```

### Response

```json
{
  "responseStatus": "SUCCESS",
  "responseMessage": "Created picklist value(s).",
  "picklistValues": [
    {
      "name": "north_america__c",
      "label": "North America"
    },
    {
      "name": "central_america__c",
      "label": "Central America"
    },
    {
      "name": "south_america__c",
      "label": "South America"
    }
  ]
}
```

Add new values to a picklist. You can add up to 2,000 values to any picklist.

### Headers

| Name | Description |
|------|-------------|
| Content-Type | application/x-www-form-urlencoded |
| Accept | application/json (default) or application/xml |

### URI Path Parameters

| Name | Description |
|------|-------------|
| {picklist_name} | The picklist name field value (license_type__v, product_family__c, region__c, etc.) |

### Request Details

To add new values, use value_1, value_2, etc., set to alphanumeric values. Enter each new picklist value label as they will be displayed in the UI. Vault uses the label to create the picklist value name.

### Response Details

| Metadata Field | Description |
|----------------|-------------|
| name | The picklist value name. This is used to reference this value in the API, and displayed to Vault Admins in the UI. |
| label | The picklist value label. Users see this label when selecting picklist values. Maximum 128 characters. |

## Update Picklist Value Label

> **Note**: Use caution when editing picklist labels or names. When these attributes are changed, they affect all existing document and object metadata that refer to the picklist. For users in the UI who are accustomed to seeing a particular selection, the changes may cause confusion. This may also break existing integrations that access picklist values via the API.

### Request

```bash
curl -X PUT -H "Authorization: {SESSION_ID}" \
    -H "Content-Type: application/x-www-form-urlencoded" \
    -d "north_america__c=North America/United States" \
    https://myvault.veevavault.com/api/v24.3/objects/picklists/regions__c
```

### Response

```json
{
  "responseStatus": "SUCCESS",
  "responseMessage": "Updated picklist value(s).",
  "picklistValues": [
    {
      "name": "north_america__c",
      "label": "North America/United States"
    }
  ]
}
```

### Headers

| Name | Description |
|------|-------------|
| Content-Type | application/x-www-form-urlencoded |
| Accept | application/json (default) or application/xml |

### URI Path Parameters

| Name | Description |
|------|-------------|
| {picklist_name} | The picklist name field value (license_type__v, product_family__c, region__c, etc.) |

### Request Details

To change an existing picklist value label, use its picklist value name set to a new label. The picklist value name will remain unchanged. For example, to change the label of the existing "north_america__c=North America", enter "north_america__c=North America/United States". You may include one or more picklist values in the request.

## Update Picklist Value

### Request

```bash
curl -X PUT -H "Authorization: {SESSION_ID}" \
    -H "Content-Type: application/x-www-form-urlencoded" \
    -d "name=north_america_united_states" \
    https://myvault.veevavault.com/api/v24.3/objects/picklists/regions__c/north_america__c
```

### Response

```json
{
  "responseStatus": "SUCCESS"
}
```

### Headers

| Name | Description |
|------|-------------|
| Content-Type | application/x-www-form-urlencoded |
| Accept | application/json (default) or application/xml |

### URI Path Parameters

| Name | Description |
|------|-------------|
| {picklist_name} | The picklist name field value (license_type__v, product_family__c, region__c, etc.) |
| {picklist_value_name} | The picklist value name field value (north_america__c, south_america__c, etc.) |

### Body Parameters

At least one of the following parameters is required:

| Name | Description |
|------|-------------|
| name (conditional) | The new name for a picklist value. This does not affect the label. Vault adds __c after processing. Special characters and double underscores __ are not allowed. |
| status (conditional) | The new status for a picklist value. Valid values are active or inactive. |

## Inactivate Picklist Value

> **Note**: If you need to inactivate a picklist value, it is best practice to use Update Picklist Value.

### Request

```bash
curl -X DELETE -H "Authorization: {SESSION_ID}" \
    https://myvault.veevavault.com/api/v24.3/objects/picklists/regions__c/north_america_united_states__c
```

### Response

```json
{
  "responseStatus": "SUCCESS",
  "responseMessage": "Inactivated picklist value.",
  "name": "north_america_united_states__c"
}
```

### Headers

| Name | Description |
|------|-------------|
| Accept | application/json (default) or application/xml |

### URI Path Parameters

| Name | Description |
|------|-------------|
| {picklist_name} | The picklist name field value (license_type__v, product_family__c, region__c, etc.) |
| {picklist_value_name} | The picklist value name field value (north_america__c, south_america__c, etc.) |
