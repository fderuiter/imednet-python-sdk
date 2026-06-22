"""TODO: Add docstring."""

from unittest.mock import Mock

import pytest

from imednet.errors import ValidationError
from imednet.validation.data_dictionary import DataDictionary
from imednet_workflows.uat.engine import EditCheckResultStatus, UATExecutionEngine


def test_uat_engine_parses_rules():
    """TODO: Add docstring."""
    dd = DataDictionary(
        business_logic=[
            {
                "Name": "Rule1",
                "Status": "Active",
                "Form": "F1",
                "Variable": "V1",
                "Operator": ">=",
                "Value": "18",
            },
            {"Name": "Rule2", "Status": "Inactive", "Form": "F2"},
        ],
        choices=[],
        forms=[],
        questions=[],
    )
    engine = UATExecutionEngine(Mock(), dd)
    assert len(engine._rules) == 1
    assert engine._rules[0]["rule_name"] == "Rule1"


def test_uat_engine_negative_generation():
    """TODO: Add docstring."""
    dd = DataDictionary(
        business_logic=[
            {
                "Name": "Rule1",
                "Status": "Active",
                "Form": "F1",
                "Variable": "V1",
                "Operator": ">=",
                "Value": "18",
            }
        ],
        choices=[],
        forms=[],
        questions=[],
    )
    engine = UATExecutionEngine(Mock(), dd)
    data = engine.generate_negative_test_case(engine._rules[0])
    assert data["V1"] == "17.0"


def test_uat_engine_run_verification():
    """TODO: Add docstring."""
    sdk = Mock()
    sdk.create_record.side_effect = ValidationError("Invalid value")

    dd = DataDictionary(
        business_logic=[
            {
                "Name": "Rule1",
                "Status": "Active",
                "Form": "F1",
                "Variable": "V1",
                "Operator": ">=",
                "Value": "18",
            }
        ],
        choices=[],
        forms=[],
        questions=[],
    )
    engine = UATExecutionEngine(sdk, dd)
    report = engine.run_verification("STUDY1")

    assert report.total_rules == 1
    assert report.passed_rules == 1
    assert report.results[0]["status"] == EditCheckResultStatus.PASS


def test_uat_engine_subject_limit():
    """TODO: Add docstring."""
    sdk = Mock()
    sdk.create_record.side_effect = ValidationError("Invalid value")

    rules = []
    for i in range(150):
        rules.append(
            {
                "Name": f"Rule{i}",
                "Status": "Active",
                "Form": "F1",
                "Variable": f"V{i}",
                "Operator": ">=",
                "Value": "18",
            }
        )

    dd = DataDictionary(business_logic=rules, choices=[], forms=[], questions=[])
    engine = UATExecutionEngine(sdk, dd)
    report = engine.run_verification("STUDY1")

    assert report.total_rules == 100
    assert report.passed_rules == 100
    assert len(report.results) == 100
