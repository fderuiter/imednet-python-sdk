# Configuration file for the Sphinx documentation builder.

import os
import sys

# Add project root directory to sys.path
sys.path.insert(0, os.path.abspath(".."))

project = "imednet-sdk"
author = "Frederick de Ruiter"
release = "0.1.0"

# Sphinx extensions
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.viewcode",
    "sphinx_autodoc_typehints",
]

# Templates and static paths
templates_path: list[str] = ["_templates"]
exclude_patterns: list[str] = []  # annotated per mypy requirement
html_static_path: list[str] = ["_static"]

import sphinx_rtd_theme  # noqa: E402

html_theme = "sphinx_rtd_theme"
html_theme_path = [sphinx_rtd_theme.get_html_theme_path()]
