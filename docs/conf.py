# Configuration file for the Sphinx documentation builder.
import os
import sys

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


# Add project root directory to sys.path
sys.path.insert(0, os.path.abspath(".."))

project = "imednet-sdk"
author = "Frederick de Ruiter"
release = "0.1.0"

# Sphinx extensions
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.viewcode",
    "sphinx.ext.napoleon",
    "sphinx_autodoc_typehints",
    "sphinx.ext.autosummary",
]

autosummary_generate = True

# Mock heavy optional dependencies so autodoc does not import them
autodoc_mock_imports = ["pandas", "numpy", "matplotlib", "pydantic"]

suppress_warnings = ["ref.ref"]

# Display type hints in the description instead of the signature to keep
# function signatures concise in the rendered documentation.
autodoc_typehints = "description"

# Templates and static paths
templates_path: list[str] = ["_templates"]
exclude_patterns: list[str] = []  # annotated per mypy requirement
html_static_path: list[str] = ["_static"]


html_theme = "sphinx_rtd_theme"
