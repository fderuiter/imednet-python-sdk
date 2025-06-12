#!/usr/bin/env bash
# Setup development environment
set -euo pipefail

poetry install --with dev
poetry run pre-commit install

echo "Development environment is ready"
