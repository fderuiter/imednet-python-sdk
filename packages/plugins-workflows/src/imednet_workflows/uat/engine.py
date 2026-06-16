from __future__ import annotations

import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional

from imednet.spi.errors import ApiError, ClientError
from imednet.spi.facade import ImednetFacade
from imednet.spi.validation import DataDictionary

logger = logging.getLogger(__name__)


class EditCheckResultStatus(str, Enum):
    PASS = "Pass"
    FAIL = "Fail"
    ERROR = "Error"
    SKIPPED = "Skipped"


@dataclass
class EditCheckVerificationReport:
    study_key: str
    total_rules: int = 0
    passed_rules: int = 0
    failed_rules: int = 0
    skipped_rules: int = 0
    results: List[Dict[str, Any]] = field(default_factory=list)


class UATExecutionEngine:
    """Automated Edit Check Verification execution engine."""

    def __init__(self, sdk: ImednetFacade, data_dictionary: DataDictionary):
        self._sdk = sdk
        self._data_dictionary = data_dictionary
        self._rules = self._parse_business_logic(data_dictionary.business_logic)

    def _parse_business_logic(self, rows: list[dict[str, str]]) -> list[dict[str, Any]]:
        rules = []
        for row in rows:
            status = row.get("Status", "Active")
            if status.lower() != "active":
                continue

            rule = {
                "rule_name": row.get("Name", row.get("rule_name", "Unknown Rule")),
                "form": row.get("Form", row.get("form", "UnknownForm")),
                "variable": row.get("Variable", row.get("variable")),
                "check_type": row.get("CheckType", row.get("check_type", "Range")),
                "operator": row.get("Operator", row.get("operator", "==")),
                "value": row.get("Value", row.get("value", "")),
                "dependency_variable": row.get(
                    "DependencyVariable", row.get("dependency_variable")
                ),
                "dependency_value": row.get("DependencyValue", row.get("dependency_value")),
                "raw": row,
            }
            rules.append(rule)
        return rules

    def generate_negative_test_case(self, rule: dict[str, Any]) -> dict[str, Any]:
        """Generate a data payload designed to violate the given rule."""
        data: dict[str, Any] = {}
        variable = rule.get("variable")
        if not variable:
            return data

        operator = rule.get("operator")
        value = rule.get("value")

        dep_var = rule.get("dependency_variable")
        dep_val = rule.get("dependency_value")

        if dep_var and dep_val:
            data[dep_var] = dep_val
            if operator == "==":
                data[variable] = f"NOT_{value}"
            elif operator == "!=":
                data[variable] = value
            else:
                data[variable] = "Invalid_Value"
        else:
            if operator == ">=":
                try:
                    if value is not None:
                        data[variable] = str(float(value) - 1)
                except (ValueError, TypeError):
                    data[variable] = "0"
            elif operator == "<=":
                try:
                    if value is not None:
                        data[variable] = str(float(value) + 1)
                except (ValueError, TypeError):
                    data[variable] = "9999"
            elif operator == "==":
                data[variable] = f"NOT_{value}"
            elif operator == "!=":
                data[variable] = value
            elif operator == "Required" or str(value).lower() == "required":
                data[variable] = ""
            else:
                data[variable] = "Invalid_Test_Value"

        return data

    def run_verification(
        self, study_key: str, form_scope: Optional[str] = None, site_name: str = "TestSite"
    ) -> EditCheckVerificationReport:
        """Run the end-to-end UAT verification against the EDC API."""
        report = EditCheckVerificationReport(study_key=study_key)

        for idx, rule in enumerate(self._rules):
            if form_scope and rule.get("form") != form_scope:
                continue

            report.total_rules += 1
            form_key = rule.get("form")

            test_data = self.generate_negative_test_case(rule)
            if not test_data:
                # If we cannot generate test data (e.g. variable is missing), mark as skipped
                report.skipped_rules += 1
                report.results.append(
                    {
                        "rule_name": rule.get("rule_name"),
                        "status": EditCheckResultStatus.SKIPPED,
                        "reason": "Missing variable for data generation",
                    }
                )
                continue

            # Use CreateNewRecordRequest format
            subject_key = f"UAT-SUBJ-{idx}"
            payload = {"formKey": form_key, "subjectKey": subject_key, "data": test_data}

            result = {
                "rule_name": rule.get("rule_name"),
                "form": form_key,
                "test_data": test_data,
                "expected_response": "Rejected",
            }

            try:
                # Submit the record. If the EDC is enforcing the business logic correctly,
                # this request should fail with a 400 ClientError (ValidationError).
                job = self._sdk.create_record(study_key, [payload])

                # If we reach here, the record was ACCEPTED by the EDC.
                # This means the edit check FAILED to catch the invalid data.
                result["actual_response"] = "Accepted"
                result["status"] = EditCheckResultStatus.FAIL
                report.failed_rules += 1
            except (ApiError, ClientError) as e:
                # 400-level errors from the API mean the request was rejected.
                # This is a SUCCESSFUL REJECTION (Pass) for negative testing.
                # Wait, if status_code is >= 500, we should log it as Error.
                status_code = getattr(e, "status_code", None)
                if status_code and status_code >= 500:
                    result["actual_response"] = f"Error: Server error {status_code}"
                    result["status"] = EditCheckResultStatus.ERROR
                    report.failed_rules += 1
                else:
                    result["actual_response"] = "Rejected"
                    result["status"] = EditCheckResultStatus.PASS
                    report.passed_rules += 1
            except Exception as e:
                result["actual_response"] = f"Error: {e}"
                result["status"] = EditCheckResultStatus.ERROR
                report.failed_rules += 1

            report.results.append(result)

            if report.total_rules >= 100:
                logger.warning("Reached maximum subject limit of 100 per UAT run.")
                break

        return report
