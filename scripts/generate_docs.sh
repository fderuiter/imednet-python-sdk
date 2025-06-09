#!/usr/bin/env bash
set -euo pipefail

sphinx-apidoc -o docs/api imednet
sphinx-build -b html docs docs/_build/html
