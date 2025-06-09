.PHONY: docs

docs:
	poetry install --with dev
	poetry run sphinx-build -b html docs docs/_build/html
