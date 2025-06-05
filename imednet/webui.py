"""Simple web UI for the iMednet SDK."""

from __future__ import annotations

import os

from flask import Flask, redirect, url_for

from .credentials import resolve_credentials
from .sdk import ImednetSDK

DEFAULT_BASE_URL = "https://edc.prod.imednetapi.com"


def _get_sdk() -> ImednetSDK:
    """Initialize the SDK using environment variables or stored credentials."""
    base_url = os.getenv("IMEDNET_BASE_URL", DEFAULT_BASE_URL)
    api_key, security_key, study_key = resolve_credentials(os.getenv("IMEDNET_CRED_PASSWORD"))
    if study_key:
        os.environ.setdefault("IMEDNET_STUDY_KEY", study_key)

    return ImednetSDK(api_key=api_key, security_key=security_key, base_url=base_url)


def create_app() -> Flask:
    """Create the Flask application."""

    app = Flask(__name__)

    @app.route("/")
    def index() -> str:
        return redirect(url_for("list_studies"))

    @app.route("/studies")
    def list_studies() -> str:
        sdk = _get_sdk()
        studies = sdk.studies.list()
        links = "".join(
            f'<li><a href="{url_for("list_subjects", study_key=s.study_key)}">'
            f"{s.study_name}</a></li>"
            for s in studies
        )
        return f"<h1>Studies</h1><ul>{links}</ul>"

    @app.route("/studies/<study_key>/subjects")
    def list_subjects(study_key: str) -> str:
        sdk = _get_sdk()
        subjects = sdk.subjects.list(study_key)
        items = "".join(f"<li>{subj.subject_key}</li>" for subj in subjects)
        return f"<h1>Subjects for {study_key}</h1><ul>{items}</ul>"

    return app


def main() -> None:
    """Run the development server."""
    create_app().run(debug=True)


if __name__ == "__main__":
    main()
