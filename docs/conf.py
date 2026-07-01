"""Sphinx configuration."""

# Configuration file for the Sphinx documentation builder.
import logging
import os
import sys
import types
import warnings

# mypy: ignore-errors
from typing import Any

"""
Configuration file for the Sphinx documentation builder.
This module contains all necessary configurations for building documentation
using Sphinx. It sets up the project information, extensions, and theme settings.
Attributes:
    project (str): The name of the project ("imednet")
    author (str): The author's name ("Frederick de Ruiter")
    release (str): The full project version from ``imednet.__version__``
    version (str): The short project version from ``imednet.__version__``
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


# Add package source roots so API modules can be imported for docs builds.
sys.path[:0] = [
    os.path.abspath("../packages/core/src"),
    os.path.abspath("../packages/providers-airflow/src"),
    os.path.abspath("../packages/plugins-workflows/src"),
    os.path.abspath("../packages/plugins-streamlit/src"),
    os.path.abspath("../packages/plugins-sinks/src"),
]
warnings.filterwarnings("ignore", message="duplicate object description*")
warnings.filterwarnings("ignore", message="Failed guarded type import*")

# Mock heavy optional dependencies so autodoc does not require them.
# Mock pandas to avoid heavy dependency while building docs. The stub provides
# minimal attributes used in type hints.
if "pandas" not in sys.modules:
    pandas_stub = types.ModuleType("pandas")

    class DataFrame:  # pragma: no cover - simple stub
        """Dummy DataFrame class."""

        pass

    def json_normalize(*args: Any, **kwargs: Any) -> DataFrame:  # type: ignore
        """Dummy json_normalize function."""
        return DataFrame()

    pandas_stub.DataFrame = DataFrame
    pandas_stub.json_normalize = json_normalize
    sys.modules["pandas"] = pandas_stub

from imednet import __version__ as imednet_version  # noqa: E402

project = "imednet"
author = "Frederick de Ruiter"
release = imednet_version
version = imednet_version

# Sphinx extensions
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.viewcode",
    "sphinx.ext.napoleon",
    "sphinx_autodoc_typehints",
    "sphinx.ext.autosummary",
    "sphinxcontrib.mermaid",
    "sphinxarg.ext",
    "sphinx.ext.doctest",
]

autosummary_generate = False

# Mock heavy optional dependencies so autodoc does not import them.
# opentelemetry is listed here so that `if TYPE_CHECKING: from opentelemetry…`
# blocks (evaluated when set_type_checking_flag=True) do not cause
# ModuleNotFoundError during the docs build.
autodoc_mock_imports = [
    "pandas",
    "numpy",
    "matplotlib",
    "airflow",
    "opentelemetry",
    "streamlit",
    "altair",
]

suppress_warnings = [
    "toc.excluded",
    "autodoc.import",
    "autodoc",
    "sphinx_autodoc_typehints",
    "app.add_directive",
]

# Sphinx 6.x does not assign a filterable type code to "duplicate object
# description" warnings, so suppress_warnings cannot catch them.  These
# duplicates arise because __init__.py files re-export symbols that are also
# documented in their own sub-module stubs.  The filter below silences them
# so the strict (-W) build is not broken by this benign re-export pattern.


class _SuppressDuplicateDescriptions(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:  # pragma: no cover
        message = record.getMessage()
        return (
            "duplicate object description" not in message
            and "Failed guarded type import" not in message
            and "more than one target found for cross-reference" not in message
        )


def setup(app: Any) -> None:  # pragma: no cover
    """Install the duplicate-description log filter after Sphinx initialises.

    Args:
        app: The Sphinx application instance (provided by Sphinx at startup).
    """
    # Sphinx wraps every internal logger as `sphinx.<module>`, e.g.
    # sphinx.domains.python becomes sphinx.sphinx.domains.python.
    suppressor = _SuppressDuplicateDescriptions()
    logging.getLogger("sphinx").addFilter(suppressor)
    logging.getLogger("sphinx.sphinx.domains.python").addFilter(suppressor)
    logging.getLogger("sphinx.sphinx_autodoc_typehints").addFilter(suppressor)


# Ignore noisy pydantic schema generation warnings.
warnings.filterwarnings("ignore", message="Failed guarded type import", category=UserWarning)

# Display type hints in the description instead of the signature to keep
# function signatures concise in the rendered documentation.
autodoc_typehints = "description"

# Autodoc default options applied to all automodule/autoclass directives.
autodoc_default_options = {
    "members": True,
    "show-inheritance": True,
}
autodoc_class_signature = "separated"

# Force sphinx-autodoc-typehints to evaluate TYPE_CHECKING blocks so that
# forward references used only under `if TYPE_CHECKING:` are resolved.
set_type_checking_flag = True

# Napoleon – enforce Google-style docstrings.
napoleon_google_docstring = True
napoleon_numpy_docstring = False
napoleon_include_init_with_doc = True

# Templates and static paths
templates_path: list[str] = ["_templates"]
exclude_patterns: list[str] = []  # annotated per mypy requirement
html_static_path: list[str] = ["_static"]


html_theme = "furo"
