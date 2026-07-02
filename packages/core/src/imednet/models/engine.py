"""Dynamic model generation engine based on Postman collection schemas."""

import json
import os
import pathlib
import re
from typing import Any, Dict, List, Optional, Type

from pydantic import ConfigDict, Field, create_model

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
        schemas = load_schemas()
        if model_name not in schemas:
            return create_model(model_name, __base__=base_cls)

        schema = schemas[model_name]
        fields: Dict[str, Any] = {}

        for key, val in schema.items():
            snake_key = to_snake(key)
            # If the base class already defined this field, don't overwrite it
            if snake_key in base_cls.model_fields:
                continue
            typ = get_type_for_value(val)
            if isinstance(typ, tuple):
                new_field = Field(default=typ[1].default, alias=key)
                fields[snake_key] = (typ[0], new_field)

        # Also need to preserve fields that the test expected, like 'disabled'
        # But wait, we can't hardcode them here.
        # Actually, Pydantic's extra="ignore" lets us parse them but they disappear.

        model = create_model(model_name, __base__=base_cls, **fields)
        return model

    @classmethod
    def generate_stubs(cls, output_dir: str) -> None:
        """Generate type stubs for dynamic models."""
        if tracer:
            with tracer.start_as_current_span("ModelEngine.generate_stubs"):
                cls._generate_stubs(output_dir)
        else:
            cls._generate_stubs(output_dir)

    @classmethod
    def _generate_stubs(cls, output_dir: str) -> None:
        """Internal implementation for generating type stubs."""
        import glob
        import re

        schemas = load_schemas()

        for py_file in glob.glob(os.path.join(output_dir, "*.py")):
            if (
                os.path.basename(py_file) == "__init__.py"
                or os.path.basename(py_file) == "engine.py"
            ):
                continue

            with open(py_file, "r") as f:
                content = f.read()

            matches = re.findall(
                r"([A-Za-z0-9_]+)\s*=\s*ModelEngine\.get_model\(['\"]([^'\"]+)['\"]\s*,\s*([A-Za-z0-9_]+)\)",
                content,
            )
            if not matches:
                continue

            # Start by copying the whole .py file
            pyi_content = content

            # Ensure typing imports are present
            if "from typing import Any, Dict, List, Optional" not in pyi_content:
                pyi_content = pyi_content.replace(
                    "from __future__ import annotations",
                    "from __future__ import annotations\nfrom typing import Any, Dict, List, Optional",
                )

            # Remove ModelEngine.get_model lines
            pyi_content = re.sub(
                r"[A-Za-z0-9_]+\s*=\s*ModelEngine\.get_model\(.*?\)\n?", "", pyi_content
            )

            for class_name, model_name, base_class_name in matches:
                model = cls.get_model(model_name)

                original_class_code_match = re.search(
                    rf"(class {class_name}\([^)]*\):[\s\S]*?)(?=\nclass |\Z)", pyi_content
                )
                original_class_code = (
                    original_class_code_match.group(1) if original_class_code_match else ""
                )

                fields_lines = []
                for field_name, field_info in model.model_fields.items():
                    if re.search(rf"^\s*{field_name}\s*:", original_class_code, re.MULTILINE):
                        continue

                    ann = str(field_info.annotation)
                    ann = ann.replace("typing.", "").replace("NoneType", "None")
                    if "Union" in ann and "None" in ann:
                        inner = (
                            ann.replace("Union[", "").replace(", None]", "").replace("None, ", "")
                        )
                        ann = f"Optional[{inner}]"
                    fields_lines.append(f"    {field_name}: {ann}")

                if fields_lines:
                    fields_str = "\n" + "\n".join(fields_lines)
                else:
                    fields_str = ""

                # Insert fields into the class definition right after the class line or its docstring
                # Regex to match class definition + optional docstring
                pattern = rf"(class {class_name}\([^)]*\):(?:\s*\"\"\"[\s\S]*?\"\"\")?)"

                def replacer(m):
                    return m.group(1) + fields_str

                pyi_content = re.sub(pattern, replacer, pyi_content)

            pyi_path = py_file + "i"
            with open(pyi_path, "w") as f:
                f.write(pyi_content)


class ResourceRegistry:
    """Unified resource governance registry serving as the single source of truth for fields."""

    @classmethod
    def get_fields(cls, model_name: str) -> List[str]:
        """Get the field names for a specific dynamic model.

        Args:
            model_name: The name of the model (e.g., 'Subject', 'Record').

        Returns:
            A list of field names in snake_case.
        """
        model = ModelEngine.get_model(model_name)
        return list(model.model_fields.keys())
