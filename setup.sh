#!/usr/bin/env bash

# Simple setup script for development
# Creates a virtual environment, installs Poetry and project dependencies,
# and configures pre-commit hooks.

set -euo pipefail

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
fi

source .venv/bin/activate

# Upgrade pip
pip install --upgrade pip >/dev/null

# Install Poetry inside the virtual environment if missing
if ! command -v poetry >/dev/null 2>&1; then
    pip install poetry >/dev/null
fi

# Install project dependencies (including dev dependencies)
poetry install --with dev

# Install pre-commit hooks
poetry run pre-commit install

echo "Setup complete. Activate the virtualenv with 'source .venv/bin/activate'"
