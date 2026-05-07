.PHONY: docs

SPHINXOPTS    ?= -W --keep-going
SPHINXBUILD   ?= sphinx-build
SPHINXAPIDOC  ?= sphinx-apidoc
APIDIR        = docs/api

docs:
	poetry install --with dev
	@echo "Cleaning old API docs..."
	rm -rf $(APIDIR)
	@echo "Generating new API docs..."
	poetry run $(SPHINXAPIDOC) -o $(APIDIR) src/imednet -f -M --tocfile index
	@echo "Building HTML..."
	poetry run $(SPHINXBUILD) -b html $(SPHINXOPTS) docs docs/_build/html
