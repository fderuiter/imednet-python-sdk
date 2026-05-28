.PHONY: docs

SPHINXOPTS    ?= -W --keep-going
SPHINXBUILD   ?= sphinx-build
SPHINXAPIDOC  ?= sphinx-apidoc
APIDIR        = docs/api

docs:
	@echo "Cleaning old API docs..."
	rm -rf $(APIDIR)
	@echo "Generating new API docs..."
	uv run $(SPHINXAPIDOC) -o $(APIDIR) packages/core/src/imednet -f -M --tocfile index
	uv run $(SPHINXAPIDOC) -o $(APIDIR) packages/providers-airflow/src/apache_airflow_providers_imednet -f -M --tocfile apache_airflow_providers_imednet_api
	uv run $(SPHINXAPIDOC) -o $(APIDIR) packages/plugins-workflows/src/imednet_workflows -f -M --tocfile imednet_workflows_api
	uv run $(SPHINXAPIDOC) -o $(APIDIR) packages/plugins-streamlit/src/imednet_streamlit -f -M --tocfile imednet_streamlit_api
	@echo "Building HTML..."
	uv run $(SPHINXBUILD) -b html $(SPHINXOPTS) docs docs/_build/html
