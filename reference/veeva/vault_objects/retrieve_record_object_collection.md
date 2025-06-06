# Retrieve Object Record Collection

## Request

```bash
curl -X GET -H "Authorization: {SESSION_ID}" \
https://myvault.veevavault.com/api/v24.3/vobjects/product__v
```

### Response

```json
{
    "responseStatus": "SUCCESS",
    "responseDetails": {
        "total": 20,
        "offset": 0,
        "limit": 200,
        "url": "/api/v24.3/vobjects/product__v",
        "object": {
            "url": "/api/v24.3/metadata/vobjects/product__v",
            "label": "Product",
            "name": "product__v",
            "label_plural": "Products",
            "prefix": "00P",
            "order": 1,
            "in_menu": true,
            "source": "standard",
            "status": [
                "active__v"
            ],
            "configuration_state": "STEADY_STATE"
        }
    },
    "data": [
        {
            "id": "00P0202",
            "name__v": "CholeCap"
        },
        {
            "id": "00P0303",
            "name__v": "Gludacta"
        },
        {
            "id": "00P0404",
            "name__v": "Nyaxa"
        }
    ]
}
```

Retrieve all records for a specific Vault Object.

**Endpoint:** `GET /api/{version}/vobjects/{object_name}`

### Headers

| Name | Description |
| ---- | ----------- |
| Accept | application/json (default) or application/xml |

### URI Path Parameters

| Name | Description |
| ---- | ----------- |
| {object_name} | The object name__v field value. For example,product__v, country__v, custom_object__c. |

### Query Parameters

| Name | Description |
| ---- | ----------- |
| fields | To specify fields to retrieve, include the parameter fields={FIELD_NAMES}. See Retrieve Specific Object Record Fields for details. |

### Response Details

The response includes the object metadata for the specified object and the id and name__v of all object records configured on the object.

| Name | Description |
| ---- | ----------- |
| configuration_state | The configuration state of your raw object. |
| | **STEADY_STATE**: This object has no pending configuration changes. |
| | **IN_DEPLOYMENT**: This object has queued or in-progress configuration changes. While in this state, Vault Admins cannot make further edits to the object configuration, and Vault users continue to interact with the Active object configuration version. In this state, you may also cancel deployment. |

## Limit, Sort, and Paginate Results

By default, Vault returns a maximum of 200 object records per page. You can change (lower) this using the limit operator. For example, to limit the number of records to 20 per page:

```bash
curl -X GET -H "Authorization: {SESSION_ID}" \
https://myvault.veevavault.com/api/v24.3/vobjects/study__v?limit=20
```

The limit operator must be a positive integer. Values over 200 are ignored.

You can change the response to sort in descending `desc` or ascending `asc` order based on an object field. For example, to sort by the name of each product in descending order:

```bash
curl -X GET -H "Authorization: {SESSION_ID}" \
https://myvault.veevavault.com/api/v24.3/vobjects/study__v?sort=name__v desc
```

With a maximum of 200 records returned per page, you must submit a new request to see the "next page" of results (when more than 200 object records exist). Vault provides two methods to accomplish pagination: the offset operator and the next_page/previous_page URLs.

The offset operator is used in request in the same way as the limit operator above. For example, if you're viewing the first page of 200 results (default maximum per page) out of 1000 total results found and want to see the next 200 results, enter offset=201.

```bash
curl -X GET -H "Authorization: {SESSION_ID}" \
https://myvault.veevavault.com/api/v24.3/vobjects/study__v?offset=201
```

The offset operator must be a positive integer. Values equaling to a number larger than the total number of records in the collection will not return any results.

To use limit, offset, and sort together, structure the string in the following manner:

```bash
curl -X GET -H "Authorization: {SESSION_ID}" \
https://myvault.veevavault.com/api/v24.3/vobjects/study__v?limit=10&offset=51&sort=name__v desc
```

The request shown above will return 10 results per page, starting with page 5 (results 51-60), and sort the results by the object record name in descending order.

Alternatively, you can use the next_page/previous_page URLs in the response to paginate results. Consider the following abridged response for an object record request:

```json
{
    "responseStatus": "SUCCESS",
    "responseDetails": {
        "total": 1000,
        "limit": 200,
        "offset": 601,
        "previous_page": "/api/v24.3/vobjects/study__v?limit=200&offset=401",
        "next_page": "/api/v24.3/vobjects/study__v?limit=200&offset=801",
        "object": {
        }
    }
}
```

There are a total of 1000 object records found. We used the default maximum of 200 records per page and offset the results to 601, meaning this response is displaying results 601-800 (page 3). Notice the next_page URL shows a limit of 200 and offset of 401 (to view page 4) and the previous_page URL shows a limit of 200 and offset of 801 (to view page 4).

The pagination URLs are automatically provided in the response when the number of records exceeds the maximum number of results per page. These strings can be used to basically "copy and paste" your next query to paginate the entire result set. The numbers at the end of the string (`?limit=200&offset=801"`) can also be modified with different limits and offsets before using the string to change the pagination.

> **Note**: The next_page and previous_page strings only remain active for about 15 minutes following the query.

## Vault-Owned user__sys Records

When you retrieve user__sys records, the response includes multiple system-owned user records that appear in all Vaults. These accounts are used to capture actions that are performed by Vault instead of by a user. These records are not included in license counts, are read-only, and cannot be referenced by another user or document. Learn more in Vault Help.

## Retrieve Specific Object Record Fields

You can augment the request to retrieve fields other than the default object record id and name__v by using the fields parameter and a comma-delimited list of object field names.

### Request

```bash
curl -X GET -H "Authorization: {SESSION_ID}" \
https://myvault.veevavault.com/api/v24.3/vobjects/product__v?fields=id,name__v,external_id__v,generic_name__c
```

### Response

```json
{
    "responseStatus": "SUCCESS",
    "responseDetails": {
        "total": 3,
        "limit": 200,
        "url": "/api/v24.3/vobjects/product__v?fields=id,name__v,external_id__v,generic_name__c",
        "object": {
            "url": "/api/v24.3/metadata/vobjects/product__v",
            "label": "Product",
            "name": "product__v"
          }
    },
    "data": [
        {
            "id": "0PR0202",
            "name__v": "CholeCap",
            "external_id__v": "CHO-PROD-0772",
            "generic_name__c": "cholepridol phosphate"
        },
        {
            "id": "0PR0303",
            "name__v": "Gludacta",
            "external_id__v": "GLU-PROD-0773",
            "generic_name__c": "glucerin sulfate"
        },
        {
            "id": "0PR0404",
            "name__v": "Nyaxa",
            "external_id__v": "NYA-PROD-0774",
            "generic_name__c": "nitroprinaline oxalate"
        }
    ]
}
```
