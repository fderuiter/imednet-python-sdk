"""Dynamic model generation engine based on manifest schemas."""

import json
import os
import re
from typing import Any, Dict, List, Optional, Type

from pydantic import ConfigDict, Field, create_model

from imednet.models.json_base import JsonModel

_CACHE: Dict[str, Dict[str, Any]] = {}

def load_schemas() -> Dict[str, Dict[str, Any]]:
    """Load API response schemas from the centralized manifest.

    Returns:
        A dictionary mapping model names to their schema definitions.
    """
    if _CACHE:
        return _CACHE

    manifest_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "manifest.json"
    )

    if not os.path.exists(manifest_path):
        return {}

    with open(manifest_path, 'r') as f:
        manifest = json.load(f)

    schemas = {}
    for resource_name, resource_def in manifest.items():
        model_name = resource_def.get("model")
        schema = resource_def.get("schema")
        if model_name and schema:
            schemas[model_name] = schema

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
    _model_cache = {}

    @classmethod
    def get_model(cls, model_name: str, base_cls: Type[Any] = JsonModel) -> Type[Any]:
        if tracer:
            with tracer.start_as_current_span("ModelEngine.get_model") as span:
                span.set_attribute("model_name", model_name)
                return cls._get_model(model_name, base_cls)
        return cls._get_model(model_name, base_cls)

    @classmethod
    def _get_model(cls, model_name: str, base_cls: Type[Any] = JsonModel) -> Type[Any]:
        if model_name in cls._model_cache:
            return cls._model_cache[model_name]
        
        schemas = load_schemas()
        if model_name not in schemas:
            model = create_model(model_name, __base__=base_cls)
            cls._model_cache[model_name] = model
            return model

        schema = schemas[model_name]
        fields: Dict[str, Any] = {}

        for key, val in schema.items():
            snake_key = to_snake(key)
            if snake_key in base_cls.model_fields:
                continue
            typ = get_type_for_value(val) if isinstance(val, str) else (Any, Field(default=None))
            if isinstance(typ, tuple):
                new_field = Field(default=typ[1].default, alias=key)
                fields[snake_key] = (typ[0], new_field)

        model = create_model(model_name, __base__=base_cls, **fields)
        cls._model_cache[model_name] = model
        return model

    @classmethod
    def generate_stubs(cls, output_dir: str) -> None:
        pass

class ResourceRegistry:
    @classmethod
    def get_fields(cls, model_name: str) -> List[str]:
        model = ModelEngine.get_model(model_name)
        return list(model.model_fields.keys())
