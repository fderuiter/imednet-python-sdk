"""Simple web UI for the iMednet SDK."""

from __future__ import annotations

import json
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
from .models.records import RegisterSubjectRequest
from .sdk import ImednetSDK
from .utils.filters import build_filter_string
from .workflows.data_extraction import DataExtractionWorkflow
from .workflows.query_management import QueryManagementWorkflow
from .workflows.register_subjects import RegisterSubjectsWorkflow

DEFAULT_BASE_URL = "https://edc.prod.imednetapi.com"


def _parse_filter_string(filter_str: str) -> dict[str, object]:
    """Parse a semicolon separated key=value string into a dictionary."""
    filter_dict: dict[str, object] = {}
    for pair in filter_str.split(";"):
        if not pair.strip() or "=" not in pair:
            continue
        key, value = pair.split("=", 1)
        val: object
        if value.lower() == "true":
            val = True
        elif value.lower() == "false":
            val = False
        elif value.isdigit():
            val = int(value)
        else:
            val = value
        filter_dict[key.strip()] = val
    return filter_dict


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
        filter_text = request.args.get("filter", "")
        filter_dict = _parse_filter_string(filter_text) if filter_text else None
        filter_str = build_filter_string(filter_dict) if filter_dict else None
        subjects = sdk.subjects.list(study_key, filter=filter_str)
        return render_template(
            "subjects.html",
            study_key=study_key,
            subjects=subjects,
            filter_text=filter_text,
        )

    @app.route("/studies/<study_key>/sites")
    def list_sites(study_key: str) -> str:
        sdk = _get_sdk()
        sites = sdk.sites.list(study_key)
        return render_template("sites.html", study_key=study_key, sites=sites)

    @app.route("/studies/<study_key>/queries/open")
    def list_open_queries(study_key: str) -> str:
        sdk = _get_sdk()
        workflow = QueryManagementWorkflow(sdk)
        queries = workflow.get_open_queries(study_key)
        return render_template(
            "queries.html",
            study_key=study_key,
            queries=queries,
        )

    @app.route("/studies/<study_key>/queries/counts")
    def query_state_counts(study_key: str) -> str:
        sdk = _get_sdk()
        workflow = QueryManagementWorkflow(sdk)
        counts = workflow.get_query_state_counts(study_key)
        return render_template(
            "query_counts.html",
            study_key=study_key,
            counts=counts,
        )

    @app.route("/studies/<study_key>/register-subjects", methods=["GET", "POST"])
    def register_subjects(study_key: str) -> Response | str:
        sdk = _get_sdk()
        workflow = RegisterSubjectsWorkflow(sdk)
        if request.method == "POST":
            data = json.loads(request.form["data"])
            subjects = [RegisterSubjectRequest.model_validate(d) for d in data]
            workflow.register_subjects(study_key=study_key, subjects=subjects)
            flash("Subjects registered")
            return redirect(url_for("list_subjects", study_key=study_key))
        return render_template("register_subjects.html", study_key=study_key)

    @app.route("/studies/<study_key>/records/extract", methods=["GET", "POST"])
    def extract_records(study_key: str) -> str:
        sdk = _get_sdk()
        workflow = DataExtractionWorkflow(sdk)
        records = None
        if request.method == "POST":
            record_filter = request.form.get("record_filter", "")
            subject_filter = request.form.get("subject_filter", "")
            visit_filter = request.form.get("visit_filter", "")
            records = workflow.extract_records_by_criteria(
                study_key,
                record_filter=(_parse_filter_string(record_filter) if record_filter else None),
                subject_filter=(_parse_filter_string(subject_filter) if subject_filter else None),
                visit_filter=(_parse_filter_string(visit_filter) if visit_filter else None),
            )
        return render_template(
            "extract_records.html",
            study_key=study_key,
            records=records,
        )

    @app.route("/users")
    def list_users() -> str:
        sdk = _get_sdk()
        include_inactive = request.args.get("include_inactive") == "1"
        users = sdk.users.list(include_inactive=include_inactive)
        return render_template("users.html", users=users, include_inactive=include_inactive)

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
