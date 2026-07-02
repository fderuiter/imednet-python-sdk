"""Aggregates and formats verification JSON reports."""

import glob
import json
import os
import sys

from imednet.models.verification import VerificationReport


def main():
    """Run aggregation."""
    report_files = glob.glob("*_report.json")
    if not report_files:
        print("No verification reports found.")
        return

    all_reports = []
    has_malformed = False

    for rf in report_files:
        with open(rf, "r") as f:
            try:
                data = json.load(f)
                all_reports.append(VerificationReport.model_validate(data))
            except Exception as e:
                print(f"::error::Failed to load malformed report {rf}: {e}")
                has_malformed = True

    if has_malformed:
        print("::error::Invalid or malformed verification reports detected.")
        sys.exit(1)

    has_drift = False
    drift_violations = []

    for r in all_reports:
        if r.status == "failed":
            has_drift = True
            for v in r.violations:
                drift_violations.append(f"- {v.violation_type} in track `{r.track}`: {v.message}")

    drift_count = len(drift_violations)

    if "GITHUB_OUTPUT" in os.environ:
        with open(os.environ["GITHUB_OUTPUT"], "a") as f:
            f.write(f"drift_detected={'true' if has_drift else 'false'}\n")
            f.write(f"drift_count={drift_count}\n")

    if has_drift:
        with open("drift_report.txt", "w") as f:
            for dv in drift_violations:
                f.write(f"{dv}\n")
        print(f"::warning:: Detected {drift_count} verification violations.")
    else:
        print("All verifications passed.")


if __name__ == "__main__":
    main()
