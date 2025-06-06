# Retrieve Object Metadata

### Request

```bash
curl -X GET -H "Authorization: {SESSION_ID}" \
https://myvault.veevavault.com/api/v24.3/metadata/vobjects/product__v
```

### Response

```json
{
    "responseStatus": "SUCCESS",
    "object": {
        "available_lifecycles": [],
        "label_plural": "Products",
        "prefix": "00P",
        "data_store": "standard",
        "description": null,
        "enable_esignatures": false,
        "source": "standard",
        "allow_attachments": false,
        "relationships": [
            {
                "relationship_name": "product_family__vr",
                "relationship_label": "Product Family",
                "field": "product_family__v",
                "relationship_type": "reference_outbound",
                "localized_data": {
                    "relationship_label": {
                        "de": "Produktfamilie",
                        "ru": "Семейство продуктов",
                        "kr": "제품군",
                        "en": "Product Family",
                        "it": "Famiglia di prodotti",
                        "pt_BR": "Família de produtos",
                        "fr": "Famille de produits",
                        "hu": "Termékcsalád",
                        "es": "Familia de productos",
                        "zh": "产品系列",
                        "zh_TW": "產品系列",
                        "th": "ตระกูลผลิตภัณฑ์",
                        "ja": "製品ファミリー",
                        "pl": "Rodzina produktów",
                        "nl": "Productgroep",
                        "tr": "Ürün Ailesi",
                        "pt_PT": "Família do produto"
                    }
                },
                "relationship_deletion": "block",
                "object": {
                    "url": "/api/v24.3/metadata/vobjects/product_family__v",
                    "label": "Product Family",
                    "name": "product_family__v",
                    "label_plural": "Product Families",
                    "prefix": "V95",
                    "localized_data": {
                        "label_plural": {
                            "de": "Produktfamilien",
                            "ru": "Семейства продуктов",
                            "kr": "제품군",
                            "en": "Product Families",
                            "it": "Famiglie di prodotti",
                            "pt_BR": "Famílias de produtos",
                            "fr": "Familles de produits",
                            "hu": "Termékcsaládok",
                            "es": "Familias de productos",
                            "zh": "产品系列",
                            "zh_TW": "產品系列",
                            "th": "ตระกูลผลิตภัณฑ์",
                            "ja": "製品ファミリー",
                            "pl": "Rodziny produktów",
                            "nl": "Productfamilies",
                            "tr": "Ürün Aileleri",
                            "pt_PT": "Famílias de produto"
                        },
                        "label": {
                            "de": "Produktfamilie",
                            "ru": "Семейство продуктов",
                            "kr": "제품군",
                            "en": "Product Family",
                            "it": "Famiglia di prodotti",
                            "pt_BR": "Família de produtos",
                            "fr": "Famille de produits",
                            "hu": "Termékcsalád",
                            "es": "Familia de productos",
                            "zh": "产品系列",
                            "zh_TW": "產品系列",
                            "th": "ตระกูลผลิตภัณฑ์",
                            "ja": "製品ファミリー",
                            "pl": "Rodzina produktów",
                            "nl": "Productgroep",
                            "tr": "Ürün Ailesi",
                            "pt_PT": "Família do produto"
                        }
                    }
                }
            }
        ],
        "urls": {
          "field": "/api/v24.3/metadata/vobjects/product__v/fields/{name}",
          "record": "/api/v24.3/vobjects/product__v/{id}",
          "list": "/api/v24.3/vobjects/product__v",
          "metadata": "/api/v24.3/metadata/vobjects/product__v"
        },
        "role_overrides": false,
        "localized_data": {
            "label_plural": {
              "de": "Produkte",
              "ru": "Продукты",
              "sv": "Produkter",
              "kr": "제품",
              "en": "Products",
              "pt_BR": "Produtos",
              "it": "Prodotti",
              "fr": "Produits",
              "hu": "Termékek",
              "es": "Productos",
              "zh": "产品",
              "zh_TW": "產品",
              "ja": "製品",
              "pl": "Produkty",
              "tr": "Ürünler",
              "nl": "Producten",
              "pt_PT": "Produtos"
            },
            "label": {
              "de": "Produkt",
              "ru": "Продукт",
              "sv": "Produkt",
              "kr": "제품",
              "en": "Product",
              "pt_BR": "Produto",
              "it": "Prodotto",
              "fr": "Produit",
              "hu": "Termék",
              "es": "Producto",
              "zh": "产品",
              "zh_TW": "產品",
              "ja": "製品",
              "pl": "Produkt",
              "tr": "Ürün",
              "nl": "Product",
              "pt_PT": "Produto"
            }
        },
        "object_class": "base",
        "order": 12,
        "allow_types": false,
        "help_content": null,
        "in_menu": true,
        "label": "Product",
        "modified_date": "2020-12-23T04:00:21.000Z",
        "created_by": 1,
        "secure_audit_trail": false,
        "secure_sharing_settings": false,
        "dynamic_security": false,
        "auditable": true,
        "name": "product__v",
        "modified_by": 1,
        "user_role_setup_object": null,
        "secure_attachments": false,
        "prevent_record_overwrite": false,
        "created_date": "2020-05-26T10:19:27.000Z",
        "system_managed": false,
        "fields": [
            {
              "help_content": null,
              "editable": false,
              "lookup_relationship_name": null,
              "description": null,
              "label": "ID",
              "source": "standard",
              "type": "ID",
              "modified_date": "2020-05-26T10:19:27.000Z",
              "created_by": 1,
              "required": false,
              "no_copy": true,
              "localized_data": {
                "label": {
                  "de": "ID",
                  "ru": "Идентификатор",
                  "sv": "ID",
                  "kr": "ID",
                  "en": "ID",
                  "pt_BR": "ID",
                  "it": "ID",
                  "fr": "ID",
                  "hu": "Azonosító",
                  "es": "ID",
                  "zh": "ID",
                  "zh_TW": "識別碼",
                  "ja": "ID",
                  "pl": "Identyfikator",
                  "tr": "Kimlik",
                  "nl": "ID",
                  "pt_PT": "ID"
                }
              },
              "name": "id",
              "list_column": false,
              "modified_by": 1,
              "facetable": false,
              "created_date": "2020-05-26T10:19:27.000Z",
              "lookup_source_field": null,
              "status": [
                "active__v"
              ],
              "order": 0
            }
          ],
          "status": [
            "active__v"
          ],
          "default_obj_type": "base__v"
  }
}
```

Retrieve all metadata configured on a standard or custom Vault Object.

**Endpoint:** `GET /api/{version}/metadata/vobjects/{object_name}`

### Headers

| Name | Description |
| ---- | ----------- |
| Accept | application/json (default) or application/xml |

### URI Path Parameters

| Name | Description |
| ---- | ----------- |
| {object_name} | The object name__v field value. For example, product__v, country__v, custom_object__c. |

### Query Parameters

| Name | Description |
| ---- | ----------- |
| loc | Set to true to retrieve the localized_data array, which contains the localized (translated) strings for the label and label_plural object fields. If omitted, defaults to false and localized Strings are not included. |

### Response Details

The response includes all metadata configured on the object, such as:

| Name | Description |
| ---- | ----------- |
| in_menu | When true, the object appears in the Vault UI's Business Admin. When configuring objects in the UI, this is the Display in Business Admin setting. |
| source | The source of this object. For example, standard objects are Veeva-supplied objects, and custom objects are objects created by your organization. |
| created_by | The user ID of the user who created this object. Standard objects are created by System, which is user ID 1. |
| fields | An array of the fields available on this object. You can Retrieve Object Field Metadata with a field's name value. |
| facetable | When true, the object is available for use as a faceted filter in the Vault UI. Learn more about faceted filters in Vault Help. |

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
