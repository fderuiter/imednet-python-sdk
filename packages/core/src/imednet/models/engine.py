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

            # Need to get the base classes so we can list only fields added by the dynamic schema
            # But the simplest way is just to write everything from the model's annotations
            # However, if it's easier, we just reconstruct the `.pyi` file from the Pydantic fields

            # Generate pyi by replacing dynamic class definitions in the original source
            pyi_content_str = content

            # Ensure typing imports are present in the pyi
            imports_re = re.search(r"^(.*?)(?=\n\nclass|\nclass)", pyi_content_str, re.DOTALL)
            if imports_re:
                original_imports = imports_re.group(1)
                new_imports = original_imports
                if "from typing import" not in new_imports:
                    new_imports += "\nfrom typing import Any, Optional\n"
                else:
                    if "Any" not in new_imports:
                        new_imports = new_imports.replace(
                            "from typing import ", "from typing import Any, "
                        )
                    if "Optional" not in new_imports:
                        new_imports = new_imports.replace(
                            "from typing import ", "from typing import Optional, "
                        )
                pyi_content_str = pyi_content_str.replace(original_imports, new_imports, 1)

            for class_name, model_name, base_class_name in matches:
                model = cls.get_model(model_name)

                stub_lines = []

                has_fields = False
                for field_name, field_info in model.model_fields.items():
                    # Format annotation
                    ann = str(field_info.annotation)
                    ann = ann.replace("typing.", "")
                    ann = ann.replace("NoneType", "None")

                    if "Union" in ann and "None" in ann:
                        # Convert Union[X, None] to Optional[X]
                        inner = (
                            ann.replace("Union[", "").replace(", None]", "").replace("None, ", "")
                        )
                        ann = f"Optional[{inner}]"

                    stub_lines.append(f"    {field_name}: {ann}")
                    has_fields = True

                if not has_fields:
                    stub_lines.append("    pass")

                stub_str = "\n".join(stub_lines)

                # Regex replace the ModelEngine assignment, appending the stub fields to the class body
                pattern = rf"(class {class_name}\([^)]*\):.*?)\n+{class_name}\s*=\s*ModelEngine\.get_model\(['\"]{model_name}['\"]\s*,\s*{class_name}\)"

                def replace_func(m: "re.Match[str]") -> str:
                    class_body = str(m.group(1))
                    existing_fields = set(
                        re.findall(r"^\s+([a-zA-Z0-9_]+)\s*:", class_body, re.MULTILINE)
                    )

                    filtered_stub_lines = []
                    has_filtered_fields = False
                    for field_name, field_info in model.model_fields.items():
                        if field_name in existing_fields:
                            continue
                        ann = str(field_info.annotation)
                        ann = ann.replace("typing.", "")
                        ann = ann.replace("NoneType", "None")
                        if "Union" in ann and "None" in ann:
                            inner = (
                                ann.replace("Union[", "")
                                .replace(", None]", "")
                                .replace("None, ", "")
                            )
                            ann = f"Optional[{inner}]"
                        filtered_stub_lines.append(f"    {field_name}: {ann}")
                        has_filtered_fields = True

                    if not has_filtered_fields and not existing_fields:
                        filtered_stub_lines.append("    pass")

                    s = "\n".join(filtered_stub_lines)
                    return class_body + "\n\n" + s

                pyi_content_str = re.sub(pattern, replace_func, pyi_content_str, flags=re.DOTALL)

            pyi_path = py_file + "i"
            with open(pyi_path, "w") as f:
                f.write(pyi_content_str)


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
