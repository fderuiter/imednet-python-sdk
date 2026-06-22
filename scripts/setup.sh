#!/usr/bin/env bash
# Setup development environment
set -euo pipefail

python3 -m pip install --upgrade pip

# Build the list of editable packages dynamically
EDITABLES=""
for package in packages/*; do
  if [ -f "$package/pyproject.toml" ]; then
    EDITABLES="$EDITABLES -e $package"
  fi
done

# Install all workspace packages and dev dependencies in one go
python3 -m pip install $EDITABLES -e ".[dev]"
pre-commit install

echo "Development environment is ready"
