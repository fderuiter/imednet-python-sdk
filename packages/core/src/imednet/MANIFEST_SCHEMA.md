# Unified Resource Manifest Schema

The `manifest.json` file controls the dynamic generation of SDK endpoints and Pydantic models. By adding a new entry to this file, the SDK will automatically expose standard synchronous and asynchronous read/write methods, without the need to define boilerplate API classes.

## Schema Structure

Each root key represents the plural API resource name (e.g., `records`, `studies`), mapping to a configuration object:

```json
{
  "resource_name": {
    "model": "ModelName",
    "operations": ["list", "get", "create"],
    "requires_study_key": true,
    "path": "custom/path/if/different/than/key",
    "id_parameter": "custom_id_param",
    "schema": {
      "fieldOne": "<string>",
      "fieldTwo": "<integer>"
    }
  }
}
```

## Fields

- **`model`** (string): The name of the Pydantic model to generate.
- **`operations`** (list of strings): Supported API operations. Can include `list`, `get`, and `create`.
- **`requires_study_key`** (boolean): Whether the API resource requires a study context to be provided during operations. Defaults to `true`.
- **`path`** (string, optional): The relative API path. If omitted, the root resource key is used.
- **`id_parameter`** (string, optional): The path parameter name used for GET requests. Defaults to `{model_name_snake_case}_id`.
- **`schema`** (object, optional): A key-value definition of the API response structure.
