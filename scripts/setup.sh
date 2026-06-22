#!/usr/bin/env bash
# Setup development environment
set -euo pipefail

python3 -m pip install --upgrade pip

# Build the list of editable packages dynamically
packages=()
for package in packages/*; do
  if [ -f "$package/pyproject.toml" ]; then
    packages+=("-e" "$package")
  fi
done

# Install all workspace packages and dev dependencies in one go
packages+=("-e" ".[dev]")
python3 -m pip install "${packages[@]}"
pre-commit install

echo "Development environment is ready"
