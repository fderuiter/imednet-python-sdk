# Interactive Setup Wizards via Standalone Bash Scripts

We adopt standalone, self-contained Bash scripts under `scripts/wizards/` for interactive developer onboarding and third-party provisioning (PyPI Trusted Publishing, iMedNet EDC credentials, CI live-testing environment). While `imednet-toolkit` is primarily a Python package with a Typer-based CLI, setup wizards must operate across external browser dashboards, write initial `.env` files, and configure GitHub secrets *before* Python virtualenvs or project dependencies are installed, without requiring runtime bootstrapping.
