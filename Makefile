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
	SPHINX_APIDOC_OPTIONS="members,show-inheritance" $(SPHINXAPIDOC) -o $(APIDIR) packages/providers-airflow/src/apache_airflow_providers_imednet -f -M --tocfile providers-airflow
	SPHINX_APIDOC_OPTIONS="members,show-inheritance" $(SPHINXAPIDOC) -o $(APIDIR) packages/plugins-workflows/src/imednet_workflows -f -M --tocfile plugins-workflows
	SPHINX_APIDOC_OPTIONS="members,show-inheritance" $(SPHINXAPIDOC) -o $(APIDIR) packages/plugins-streamlit/src/imednet_streamlit -f -M --tocfile plugins-streamlit
	SPHINX_APIDOC_OPTIONS="members,show-inheritance" $(SPHINXAPIDOC) -o $(APIDIR) packages/plugins-sinks/src/imednet_sinks -f -M --tocfile plugins-sinks

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
