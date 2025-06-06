# Retrieve Limits on Objects

Retrieve the limits on object record creation and custom object creation in your Vault.

## Request

```bash
curl -X GET -H "Authorization: {SESSION_ID}" \
https://myvault.veevavault.com/api/v24.3/limits
```

## Response

```json
{
  "responseStatus": "SUCCESS",
  "data": [
    {
      "name": "records_per_object",
      "max": 1000000
    },
    {
      "name": "custom_objects",
      "remaining": 7,
      "max": 20
    }
  ]
}
```

## Details

Vault limits the number of object records that can be created for each object (product__v, study__v, custom_object__c, etc.). There is also a limit to the number of custom objects that can be created in each Vault.

### Endpoint

`GET /api/{version}/limits`

### Headers

| Name | Description |
|------|-------------|
| Accept | application/json (default) or application/xml |

### Response Fields

| Field Name | Description |
|------------|-------------|
| records_per_object | The maximum number of records that can be created per object in the Vault. |
| custom_objects | The maximum number of custom objects that can be created in the Vault and the number remaining. |