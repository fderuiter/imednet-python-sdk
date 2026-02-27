.PHONY: docs

docs:
	poetry install --with dev
	poetry run sphinx-apidoc -o docs src/imednet \
	    src/imednet/core/__init__.py src/imednet/models/base.py
	poetry run sphinx-build -b html --keep-going docs docs/_build/html
