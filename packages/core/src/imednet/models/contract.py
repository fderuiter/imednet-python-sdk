"""Unified contract definitions."""

import json
import os
import re
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class FieldDefinition(BaseModel):
    """Internal contract for a model field."""

    name: str
    type_name: str
    default_value: Any = None
    alias: Optional[str] = None


class ModelDefinition(BaseModel):
    """Internal contract for a model."""

    name: str
    fields: Dict[str, FieldDefinition]


class APIContract(BaseModel):
    """Unified API Contract."""

    models: Dict[str, ModelDefinition] = Field(default_factory=dict)


def to_snake(name: str) -> str:
    """Convert camelCase or PascalCase strings to snake_case."""
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()


class ContractBuilder:
    """Builder for APIContract."""

    def __init__(self) -> None:
        """Initialize."""
        self.contract = APIContract()

    def parse_postman_type(self, val: Any) -> tuple[str, Any]:
        """Map Postman placeholder strings to internal type names and defaults."""
        if isinstance(val, str):
            if val == "<string>":
                return "string", ""
            if val == "<integer>":
                return "integer", 0
            if val == "<boolean>":
                return "boolean", False
        return "any", None

    def ingest_postman(self, file_path: str) -> None:
        """Ingest a Postman collection JSON file."""
        if not os.path.exists(file_path):
            return

        with open(file_path, 'r') as f:
            data = json.load(f)

        if not isinstance(data, dict):
            return

        name_mapping = {
            "Study information": "Study",
            "List of forms": "Form",
            "Variable list": "Variable",
            "Interval list": "Interval",
            "Site list": "Site",
            "Subject list": "Subject",
            "Record list": "Record",
            "Job created": "Job",
            "Job status": "JobStatus",
            "Record revision list": "RecordRevision",
            "Coding list": "Coding",
            "Query list": "Query",
            "Visit list": "Visit",
            "User list": "User",
        }

        def extract_schemas(items: List[Dict[str, Any]]) -> None:
            if not isinstance(items, list):
                return
            for item in items:
                if not isinstance(item, dict):
                    continue
                if 'item' in item:
                    extract_schemas(item['item'])
                elif 'response' in item:
                    if not isinstance(item['response'], list):
                        continue
                    for resp in item['response']:
                        if not isinstance(resp, dict):
                            continue
                        if resp.get('name') in name_mapping and 'body' in resp:
                            body = resp['body']
                            if body and isinstance(body, str):
                                try:
                                    parsed = json.loads(body)
                                    if not isinstance(parsed, dict):
                                        continue
                                    model_name = name_mapping[resp['name']]
                                    schema_dict = None
                                    if (
                                        'data' in parsed
                                        and isinstance(parsed['data'], list)
                                        and len(parsed['data']) > 0
                                    ):
                                        schema_dict = parsed['data'][0]
                                    elif 'data' not in parsed and 'metadata' not in parsed:
                                        schema_dict = parsed

                                    if schema_dict:
                                        fields = {}
                                        for key, val in schema_dict.items():
                                            snake_key = to_snake(key)
                                            type_name, default_value = self.parse_postman_type(val)
                                            fields[snake_key] = FieldDefinition(
                                                name=snake_key,
                                                type_name=type_name,
                                                default_value=default_value,
                                                alias=key,
                                            )
                                        self.contract.models[model_name] = ModelDefinition(
                                            name=model_name, fields=fields
                                        )
                                except Exception:
                                    pass

        extract_schemas(data.get('item', []))

    def ingest_openapi(self, file_path: str) -> None:
        """Ingest an OpenAPI specification JSON file."""
        if not os.path.exists(file_path):
            return

        with open(file_path, 'r') as f:
            data = json.load(f)

        if not isinstance(data, dict):
            return

        components = data.get("components", {})
        schemas = components.get("schemas", {})

        for model_name, schema in schemas.items():
            if schema.get("type") == "object":
                properties = schema.get("properties", {})
                fields = {}
                for key, prop in properties.items():
                    snake_key = to_snake(key)

                    type_name = "any"
                    default_value = None
                    prop_type = prop.get("type")
                    if prop_type == "string":
                        type_name = "string"
                        default_value = ""
                    elif prop_type == "integer":
                        type_name = "integer"
                        default_value = 0  # type: ignore
                    elif prop_type == "boolean":
                        type_name = "boolean"
                        default_value = False  # type: ignore

                    fields[snake_key] = FieldDefinition(
                        name=snake_key,
                        type_name=type_name,
                        default_value=default_value,
                        alias=key,
                    )

                self.contract.models[model_name] = ModelDefinition(name=model_name, fields=fields)

    def ingest_manifest(self, file_path: str) -> None:
        """Ingest models from the unified resource manifest."""
        if not os.path.exists(file_path):
            return

        with open(file_path, 'r') as f:
            data = json.load(f)

        if not isinstance(data, dict):
            return

        for resource_name, resource_def in data.items():
            model_name = resource_def.get("model")
            schema_dict = resource_def.get("schema")
            if model_name and schema_dict:
                fields = {}
                for key, val in schema_dict.items():
                    snake_key = to_snake(key)
                    type_name, default_value = self.parse_postman_type(val)
                    fields[snake_key] = FieldDefinition(
                        name=snake_key,
                        type_name=type_name,
                        default_value=default_value,
                        alias=key,
                    )
                self.contract.models[model_name] = ModelDefinition(
                    name=model_name, fields=fields
                )
