.PHONY: docs

docs:
	poetry install --with dev
	poetry run sphinx-apidoc -o docs imednet \
	    imednet/core/__init__.py imednet/models/base.py
	poetry run sphinx-build -b html -W --keep-going docs docs/_build/html
