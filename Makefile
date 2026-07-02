.PHONY: docs doctest test-containers apidocs validate-diagrams

SPHINXOPTS    ?= -W --keep-going
SPHINXBUILD   ?= sphinx-build
SPHINXAPIDOC  ?= sphinx-apidoc
APIDIR        = docs/api

test-containers:
	@echo "Starting ephemeral containerized databases..."
	docker compose up -d
	@echo "Waiting for databases to initialize..."
	sleep 15
	@echo "Running integration tests..."
	IMEDNET_TEST_CONTAINERS=1 pytest packages/plugins-sinks/tests/integration/test_containerized_sinks.py -v; \
	status=$$?; \
	echo "Cleaning up containers..."; \
	docker compose down -v; \
	exit $$status

apidocs:
	@echo "Cleaning old API docs..."
	rm -rf $(APIDIR)
	@echo "Generating new API docs..."
	SPHINX_APIDOC_OPTIONS="members,show-inheritance" $(SPHINXAPIDOC) -o $(APIDIR) packages/core/src/imednet packages/core/src/imednet/core packages/core/src/imednet/compat packages/core/src/imednet/http -f -M --tocfile core
	@for pkg in packages/*; do \
		if [ "$$pkg" != "packages/core" ] && [ -d "$$pkg/src" ]; then \
			pkg_name=$$(basename $$pkg); \
			src_dir=$$(ls -d $$pkg/src/* | head -n 1); \
			SPHINX_APIDOC_OPTIONS="members,show-inheritance" $(SPHINXAPIDOC) -o $(APIDIR) $$src_dir -f -M --tocfile $$pkg_name; \
		fi \
	done

validate-diagrams:
	@echo "Validating mermaid diagrams..."
	python scripts/validate_diagrams.py

docs: apidocs validate-diagrams validate-docs
	@echo "Building HTML..."
	$(SPHINXBUILD) -b html $(SPHINXOPTS) docs docs/_build/html

doctest: apidocs
	@echo "Type-checking documentation snippets..."
	python scripts/typecheck_docs.py
	@echo "Running Sphinx doctests..."
	$(SPHINXBUILD) -b doctest $(SPHINXOPTS) docs docs/_build/doctest

validate-docs:
	@echo "Validating documentation..."
	python scripts/validate_docs.py
