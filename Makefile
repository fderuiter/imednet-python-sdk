.PHONY: docs test-containers

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
	IMEDNET_TEST_CONTAINERS=1 poetry run pytest packages/plugins-sinks/tests/integration/test_containerized_sinks.py -v; \
	status=$$?; \
	echo "Cleaning up containers..."; \
	docker compose down -v; \
	exit $$status

docs:
	@echo "Cleaning old API docs..."
	rm -rf $(APIDIR)
	@echo "Generating new API docs..."
	poetry run $(SPHINXAPIDOC) -o $(APIDIR) packages/core/src/imednet packages/core/src/imednet/core packages/core/src/imednet/compat packages/core/src/imednet/http -f -M --tocfile index
	poetry run $(SPHINXAPIDOC) -o $(APIDIR) packages/providers-airflow/src/apache_airflow_providers_imednet -f -M --tocfile apache_airflow_providers_imednet_api
	poetry run $(SPHINXAPIDOC) -o $(APIDIR) packages/plugins-workflows/src/imednet_workflows -f -M --tocfile imednet_workflows_api
	poetry run $(SPHINXAPIDOC) -o $(APIDIR) packages/plugins-streamlit/src/imednet_streamlit -f -M --tocfile imednet_streamlit_api
	@echo "Building HTML..."
	poetry run $(SPHINXBUILD) -b html $(SPHINXOPTS) docs docs/_build/html
