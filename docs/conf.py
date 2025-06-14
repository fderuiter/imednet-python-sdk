# Configuration file for the Sphinx documentation builder.
import os
import sys
import types
from typing import Any

"""
Configuration file for the Sphinx documentation builder.
This module contains all necessary configurations for building documentation
using Sphinx. It sets up the project information, extensions, and theme settings.
Attributes:
    project (str): The name of the project ("imednet-sdk")
    author (str): The author's name ("Frederick de Ruiter")
    release (str): The version of the project ("0.1.0")
    extensions (list): List of Sphinx extensions to be used
    templates_path (list[str]): Path to custom templates
    exclude_patterns (list[str]): Patterns to exclude from documentation
    html_static_path (list[str]): Path to static files
    html_theme (str): The HTML theme to be used ("sphinx_rtd_theme")
    html_theme_path (list): Path to the HTML theme
Note:
    This configuration uses the Read the Docs theme and includes support for
    automatic documentation generation from docstrings and type hints.
"""


# Add project root directory to sys.path so `imednet` can be imported
sys.path.insert(0, os.path.abspath(".."))

# Mock heavy optional dependencies so autodoc does not require them.
# Mock pandas to avoid heavy dependency while building docs. The stub provides
# minimal attributes used in type hints.
if "pandas" not in sys.modules:
    pandas_stub = types.ModuleType("pandas")

    class DataFrame:  # pragma: no cover - simple stub
        pass

    def json_normalize(*args: Any, **kwargs: Any) -> DataFrame:  # type: ignore
        return DataFrame()

    pandas_stub.DataFrame = DataFrame
    pandas_stub.json_normalize = json_normalize
    sys.modules["pandas"] = pandas_stub

for mod in ["numpy", "matplotlib"]:
    if mod not in sys.modules:
        sys.modules[mod] = types.ModuleType(mod)


class _DummyModule(types.ModuleType):
    """Simple module that auto-creates nested modules."""

    def __getattr__(self, name: str) -> types.ModuleType:  # pragma: no cover - docs
        fullname = f"{self.__name__}.{name}"
        mod = _DummyModule(fullname)
        sys.modules[fullname] = mod
        return mod


if "airflow" not in sys.modules:
    airflow_stub = _DummyModule("airflow")
    airflow_stub.models = _DummyModule("airflow.models")
    airflow_stub.models.BaseOperator = object
    airflow_stub.hooks = _DummyModule("airflow.hooks")
    airflow_stub.hooks.base = _DummyModule("airflow.hooks.base")
    airflow_stub.hooks.base.BaseHook = object
    airflow_stub.operators = _DummyModule("airflow.operators")
    airflow_stub.export_operator = _DummyModule("airflow.export_operator")
    airflow_stub.exceptions = _DummyModule("airflow.exceptions")
    airflow_stub.exceptions.AirflowException = Exception
    airflow_stub.providers = _DummyModule("airflow.providers")
    sys.modules.update(
        {
            "airflow": airflow_stub,
            "airflow.models": airflow_stub.models,
            "airflow.hooks": airflow_stub.hooks,
            "airflow.hooks.base": airflow_stub.hooks.base,
            "airflow.operators": airflow_stub.operators,
            "airflow.export_operator": airflow_stub.export_operator,
            "airflow.exceptions": airflow_stub.exceptions,
            "airflow.providers": airflow_stub.providers,
        }
    )

from imednet import __version__ as imednet_version  # noqa: E402

project = "imednet-sdk"
author = "Frederick de Ruiter"
release = imednet_version

# Sphinx extensions
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.viewcode",
    "sphinx.ext.napoleon",
    "sphinx_autodoc_typehints",
    "sphinx.ext.autosummary",
    "sphinxcontrib.mermaid",
]

autosummary_generate = True

# Mock heavy optional dependencies so autodoc does not import them
autodoc_mock_imports = ["pandas", "numpy", "matplotlib", "pydantic", "airflow"]

suppress_warnings = ["ref.ref", "autodoc", "autodoc.import_object"]

# Display type hints in the description instead of the signature to keep
# function signatures concise in the rendered documentation.
autodoc_typehints = "description"

# Templates and static paths
templates_path: list[str] = ["_templates"]
exclude_patterns: list[str] = [
    "imednet.airflow.rst",
    "imednet.cli.rst",
    "imednet.integrations.rst",
    "imednet.validation.rst",
]  # annotated per mypy requirement
html_static_path: list[str] = ["_static"]


html_theme = "sphinx_rtd_theme"
