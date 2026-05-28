#!/usr/bin/env bash
# Setup development environment
set -euo pipefail

uv sync --with dev
uv run pre-commit install

echo "Development environment is ready"
