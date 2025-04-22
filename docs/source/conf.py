# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import os
import sys

sys.path.insert(0, os.path.abspath("../../"))  # Add project root to path

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "imednet-python-sdk"  # Match pyproject.toml
copyright = "2025, Frederick de Ruiter"
author = "Frederick de Ruiter"
release = "0.1.0"  # Match pyproject.toml

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.autodoc",  # Core library for html generation from docstrings
    "sphinx.ext.napoleon",  # Support for Google and NumPy style docstrings
    "sphinx.ext.viewcode",  # Add links to highlighted source code
    "sphinx.ext.intersphinx",  # Link to other projects' documentation
    "sphinx.ext.githubpages",  # Support for GitHub Pages
    "sphinx_rtd_theme",  # Read the Docs theme
    "sphinx_autodoc_typehints",  # Automatically document typehints
    "sphinx_copybutton",  # Add a 'copy to clipboard' button to code blocks
]

templates_path = ["_templates"]
exclude_patterns = []

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "sphinx_rtd_theme"
html_static_path = ["_static"]

# -- Extension configuration -------------------------------------------------

# Napoleon settings (Google style)
napoleon_google_docstring = True
napoleon_numpy_docstring = False  # We are using Google style
napoleon_include_init_with_doc = True
napoleon_include_private_with_doc = False
napoleon_include_special_with_doc = True
napoleon_use_admonition_for_examples = False
napoleon_use_admonition_for_notes = False
napoleon_use_admonition_for_references = False
napoleon_use_ivar = False
napoleon_use_param = True
napoleon_use_rtype = True
napoleon_preprocess_types = False
napoleon_type_aliases = None
napoleon_attr_annotations = True

# Intersphinx mapping
intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "pydantic": ("https://docs.pydantic.dev/latest/", None),
}

# Autodoc settings
autodoc_member_order = "bysource"
autodoc_default_options = {
    "members": True,
    "member-order": "bysource",
    "special-members": "__init__",
    "undoc-members": True,
    "exclude-members": "__weakref__",
}

# Typehints settings
set_type_checking_flag = True  # Enable type checking for typehints
typehints_fully_qualified = False  # Don't show full path for types
always_document_param_types = True  # Ensure param types are documented

# Copybutton settings
copybutton_prompt_text = r">>> |\.\.\. |\$ "  # Regex to exclude prompts
copybutton_prompt_is_regexp = True
