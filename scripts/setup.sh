#!/usr/bin/env bash

# Setup script for iMedNet Python SDK development environment

set -euo pipefail

# Ensure Python 3 is available
if ! command -v python3 >/dev/null 2>&1; then
  echo "Python 3 is required" >&2
  exit 1
fi

# Install Poetry if not already installed
if ! command -v poetry >/dev/null 2>&1; then
  echo "Installing Poetry..."
  curl -sSL https://install.python-poetry.org | python3 -
  export PATH="$HOME/.local/bin:$PATH"
fi

# Install project dependencies including development extras
poetry install --with dev

# Install pre-commit hooks
poetry run pre-commit install

echo "Environment setup complete. Activate with 'poetry shell'."
