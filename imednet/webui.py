"""Simple web UI for the iMednet SDK."""

from __future__ import annotations

import os
from pathlib import Path

from flask import (
    Flask,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)
from werkzeug.wrappers import Response

from .credentials import resolve_credentials, save_credentials
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

    template_dir = Path(__file__).with_name("templates")
    app = Flask(__name__, template_folder=str(template_dir))
    app.secret_key = os.environ.get("FLASK_SECRET", "dev")

    @app.route("/")
    def index() -> Response:
        """Redirect to the studies listing."""
        return redirect(url_for("list_studies"))

    @app.route("/studies")
    def list_studies() -> str:
        sdk = _get_sdk()
        studies = sdk.studies.list()
        return render_template("studies.html", studies=studies)

    @app.route("/studies/<study_key>/subjects")
    def list_subjects(study_key: str) -> str:
        sdk = _get_sdk()
        subjects = sdk.subjects.list(study_key)
        return render_template(
            "subjects.html",
            study_key=study_key,
            subjects=subjects,
        )

    @app.route("/studies/<study_key>/sites")
    def list_sites(study_key: str) -> str:
        sdk = _get_sdk()
        sites = sdk.sites.list(study_key)
        return render_template("sites.html", study_key=study_key, sites=sites)

    @app.route("/users")
    def list_users() -> str:
        sdk = _get_sdk()
        users = sdk.users.list()
        return render_template("users.html", users=users)

    @app.route("/credentials", methods=["GET", "POST"])
    def credentials_form() -> Response | str:
        if request.method == "POST":
            save_credentials(
                request.form["api_key"],
                request.form["security_key"],
                request.form.get("study_key", ""),
                request.form["password"],
            )
            flash("Credentials saved")
            return redirect(url_for("list_studies"))
        return render_template("credentials.html")

    return app


def main() -> None:
    """Run the development server."""
    create_app().run(debug=True)


if __name__ == "__main__":
    main()
