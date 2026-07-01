"""Dynamic model generation engine based on Postman collection schemas."""

import json
import os
import pathlib
import re
from typing import Any, Dict, List, Optional, Type

from msgspec import field as Field

from imednet.models.json_base import JsonModel

_CACHE: Dict[str, Dict[str, Any]] = {}


def load_schemas() -> Dict[str, Dict[str, Any]]:
    """Load API response schemas from the iMedNet Postman collection.

    Returns:
        A dictionary mapping model names to their schema definitions.
    """
    if _CACHE:
        return _CACHE

    postman_path = os.environ.get("IMEDNET_POSTMAN_PATH")
    if not postman_path:
        local_dev_path = os.path.join(
            os.path.dirname(
                os.path.dirname(
                    os.path.dirname(
                        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
                    )
                )
            ),
            "imednet.postman_collection.json",
        )
        if os.path.exists(local_dev_path):
            postman_path = local_dev_path
        else:
            postman_path = "/app/imednet.postman_collection.json"

    if not os.path.exists(postman_path):
        return {}

    with open(postman_path, 'r') as f:
        data = json.load(f)

    schemas: Dict[str, Dict[str, Any]] = {}

    if not isinstance(data, dict):
        return schemas

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
        """Recursively extract schemas from Postman collection items."""
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
                                if (
                                    'data' in parsed
                                    and isinstance(parsed['data'], list)
                                    and len(parsed['data']) > 0
                                ):
                                    schemas[model_name] = parsed['data'][0]
                                elif not 'data' in parsed and not 'metadata' in parsed:
                                    schemas[model_name] = parsed
                            except Exception:
                                pass

    extract_schemas(data.get('item', []))
    _CACHE.update(schemas)
    return schemas


def get_type_for_value(val: str) -> Any:
    """Map Postman placeholder strings to Python types and default values."""
    if val == "<string>":
        return (Optional[str], Field(default=""))
    if val == "<integer>":
        return (Optional[int], Field(default=0))
    if val == "<boolean>":
        return (Optional[bool], Field(default=False))
    return (Any, Field(default=None))


def to_snake(name: str) -> str:
    """Convert camelCase or PascalCase strings to snake_case."""
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()


try:
    from opentelemetry import trace as _trace

    tracer: Any = _trace.get_tracer(__name__)
except Exception:
    tracer = None


class ModelEngine:
    """Engine for dynamically creating Pydantic models from schemas."""

    @classmethod
    def get_model(cls, model_name: str, base_cls: Type[Any] = JsonModel) -> Type[Any]:
        """Get or create a dynamic Pydantic model for the given name.

        Args:
            model_name: The name of the model (e.g., 'Subject', 'Record').
            base_cls: The base class to inherit from.

        Returns:
            A Pydantic model class.
        """
        if tracer:
            with tracer.start_as_current_span("ModelEngine.get_model") as span:
                span.set_attribute("model_name", model_name)
                return cls._get_model(model_name, base_cls)
        return cls._get_model(model_name, base_cls)

    @classmethod
    def _get_model(cls, model_name: str, base_cls: Type[Any] = JsonModel) -> Type[Any]:
        """Internal implementation for dynamic model creation."""
        import msgspec
        schemas = load_schemas()
        if model_name not in schemas:
            return msgspec.defstruct(model_name, [], bases=(base_cls,), kw_only=True, omit_defaults=True)

        schema = schemas[model_name]
        fields = []

        for key, val in schema.items():
            snake_key = to_snake(key)
            # If the base class already defined this field, don't overwrite it
            if snake_key in [f.name for f in msgspec.structs.fields(base_cls)]:
                continue
            typ = get_type_for_value(val)
            if isinstance(typ, tuple):
                new_field = Field(default=typ[1].default, name=key)
                fields.append((snake_key, typ[0], new_field))

        model = msgspec.defstruct(model_name, fields, bases=(base_cls,), kw_only=True, omit_defaults=True)
        return model

    @classmethod
    def generate_stubs(cls, output_dir: str) -> None:
        """Generate type stubs for dynamic models (placeholder)."""
        if tracer:
            with tracer.start_as_current_span("ModelEngine.generate_stubs"):
                pass
        else:
            pass
