"""Unit tests for SyntheticRecordGenerator."""

from datetime import date
from unittest.mock import MagicMock

import pytest

from imednet_workflows.uat.generator import GeneratedRecordSet, SyntheticRecordGenerator
from imednet_workflows.uat.inspector import StudySnapshot
from imednet_workflows.uat.models import (
    RecordTestType,
    UATFormSpec,
    UATSpecification,
    UATSubjectSpec,
    UATVariableSpec,
    VariableTestStrategy,
)


@pytest.fixture
def mock_snapshot():
    """Fixture for StudySnapshot mock."""
    snapshot = MagicMock(spec=StudySnapshot)
    snapshot.active_sites.return_value = [MagicMock(site_name="Test Site")]
    return snapshot


@pytest.fixture
def basic_spec():
    """Fixture for basic UATSpecification."""
    return UATSpecification(
        study_key="STUDY01",
        study_name="Test Study",
        subject_specs=[
            UATSubjectSpec(
                site_name="Test Site", subject_count=2, subject_key_prefix="SUBJ-"
            )
        ],
        form_specs=[
            UATFormSpec(
                form_key="F_REG",
                form_name="Registration",
                form_type="Enrollment",
                test_type=RecordTestType.REGISTER_SUBJECT,
                subject_count=1,
                variables=[
                    UATVariableSpec(
                        variable_name="SUBJID",
                        variable_key="V1",
                        variable_type="Text",
                        form_key="F_REG",
                        strategy=VariableTestStrategy.SYNTHETIC,
                        max_length=5,
                    )
                ],
            )
        ],
    )


def test_generate_registration(basic_spec, mock_snapshot):
    """Test subject registration generation."""
    generator = SyntheticRecordGenerator(seed=42)
    results = generator.generate(basic_spec, mock_snapshot)

    assert len(results) == 1
    res = results[0]
    assert res.form_key == "F_REG"
    assert len(res.payloads) == 1
    assert res.payloads[0]["formKey"] == "F_REG"
    assert res.payloads[0]["siteName"] == "Test Site"
    assert "SUBJID" in res.payloads[0]["data"]
    assert len(res.payloads[0]["data"]["SUBJID"]) == 5


def test_fixed_strategy(mock_snapshot):
    """Test FIXED strategy generation."""
    spec = UATSpecification(
        study_key="S1",
        study_name="S1",
        form_specs=[
            UATFormSpec(
                form_key="F1",
                form_name="F1",
                form_type="Standard",
                test_type=RecordTestType.CREATE_NEW_RECORD,
                subject_count=1,
                variables=[
                    UATVariableSpec(
                        variable_name="VAR1",
                        variable_key="V1",
                        variable_type="Text",
                        form_key="F1",
                        strategy=VariableTestStrategy.FIXED,
                        fixed_value="FIXED_VAL",
                    )
                ],
            )
        ],
    )
    generator = SyntheticRecordGenerator()
    results = generator.generate(spec, mock_snapshot)
    assert results[0].payloads[0]["data"]["VAR1"] == "FIXED_VAL"


def test_skip_strategy(mock_snapshot):
    """Test SKIP strategy generation."""
    spec = UATSpecification(
        study_key="S1",
        study_name="S1",
        form_specs=[
            UATFormSpec(
                form_key="F1",
                form_name="F1",
                form_type="Standard",
                test_type=RecordTestType.CREATE_NEW_RECORD,
                subject_count=1,
                variables=[
                    UATVariableSpec(
                        variable_name="VAR1",
                        variable_key="V1",
                        variable_type="Text",
                        form_key="F1",
                        strategy=VariableTestStrategy.SKIP,
                    )
                ],
            )
        ],
    )
    generator = SyntheticRecordGenerator()
    results = generator.generate(spec, mock_snapshot)
    assert "VAR1" not in results[0].payloads[0]["data"]


def test_boundary_strategy(mock_snapshot):
    """Test BOUNDARY strategy generation."""
    spec = UATSpecification(
        study_key="S1",
        study_name="S1",
        form_specs=[
            UATFormSpec(
                form_key="F1",
                form_name="F1",
                form_type="Standard",
                test_type=RecordTestType.CREATE_NEW_RECORD,
                subject_count=1,  # Boundary generates 2 payloads regardless
                variables=[
                    UATVariableSpec(
                        variable_name="NUM",
                        variable_key="V1",
                        variable_type="Number",
                        form_key="F1",
                        strategy=VariableTestStrategy.BOUNDARY,
                        min_value=10,
                        max_value=20,
                    )
                ],
            )
        ],
    )
    generator = SyntheticRecordGenerator()
    results = generator.generate(spec, mock_snapshot)
    assert len(results[0].payloads) == 2
    assert results[0].payloads[0]["data"]["NUM"] == "10.0"
    assert results[0].payloads[1]["data"]["NUM"] == "20.0"


def test_coded_all_strategy(mock_snapshot):
    """Test CODED_ALL strategy generation."""
    spec = UATSpecification(
        study_key="S1",
        study_name="S1",
        form_specs=[
            UATFormSpec(
                form_key="F1",
                form_name="F1",
                form_type="Standard",
                test_type=RecordTestType.CREATE_NEW_RECORD,
                subject_count=1,
                variables=[
                    UATVariableSpec(
                        variable_name="CODED",
                        variable_key="V1",
                        variable_type="Coded",
                        form_key="F1",
                        strategy=VariableTestStrategy.CODED_ALL,
                        coded_values=["A", "B", "C"],
                    )
                ],
            )
        ],
    )
    generator = SyntheticRecordGenerator()
    results = generator.generate(spec, mock_snapshot)
    assert len(results[0].payloads) == 3
    assert results[0].payloads[0]["data"]["CODED"] == "A"
    assert results[0].payloads[1]["data"]["CODED"] == "B"
    assert results[0].payloads[2]["data"]["CODED"] == "C"


def test_coded_all_warning(mock_snapshot):
    """Test CODED_ALL warning path."""
    spec = UATSpecification(
        study_key="S1",
        study_name="S1",
        form_specs=[
            UATFormSpec(
                form_key="F1",
                form_name="F1",
                form_type="Standard",
                test_type=RecordTestType.CREATE_NEW_RECORD,
                subject_count=1,
                variables=[
                    UATVariableSpec(
                        variable_name="C1",
                        variable_key="V1",
                        variable_type="Coded",
                        form_key="F1",
                        strategy=VariableTestStrategy.CODED_ALL,
                        coded_values=["A", "B"],
                    ),
                    UATVariableSpec(
                        variable_name="C2",
                        variable_key="V2",
                        variable_type="Coded",
                        form_key="F1",
                        strategy=VariableTestStrategy.CODED_ALL,
                        coded_values=["X", "Y"],
                    ),
                ],
            )
        ],
    )
    generator = SyntheticRecordGenerator()
    results = generator.generate(spec, mock_snapshot)
    assert len(results[0].warnings) > 0
    assert len(results[0].payloads) == 1  # Fallback to 1 subject


def test_seed_reproducibility(basic_spec, mock_snapshot):
    """Test reproducibility with random seed."""
    gen1 = SyntheticRecordGenerator(seed=123)
    res1 = gen1.generate(basic_spec, mock_snapshot)

    gen2 = SyntheticRecordGenerator(seed=123)
    res2 = gen2.generate(basic_spec, mock_snapshot)

    assert res1[0].payloads[0]["data"] == res2[0].payloads[0]["data"]


def test_faker_missing_error(basic_spec, mock_snapshot, monkeypatch):
    """Test error when Faker is missing."""
    import imednet_workflows.uat.generator as generator_mod

    monkeypatch.setattr(generator_mod, "Faker", None)

    # We need to re-instantiate or bypass the check in __init__ if we want to test _get_faker
    # Actually SyntheticRecordGenerator.__init__ checks Faker is not None.

    generator = SyntheticRecordGenerator()
    monkeypatch.setattr(generator, "_faker", None)

    with pytest.raises(ImportError, match="faker is required"):
        generator._get_faker()


def test_various_types(mock_snapshot):
    """Test generation across various variable types."""
    spec = UATSpecification(
        study_key="S1",
        study_name="S1",
        global_date_value=date(2023, 1, 1),
        form_specs=[
            UATFormSpec(
                form_key="F1",
                form_name="F1",
                form_type="Standard",
                test_type=RecordTestType.CREATE_NEW_RECORD,
                subject_count=1,
                variables=[
                    UATVariableSpec(
                        variable_name="N",
                        variable_key="V1",
                        variable_type="Number",
                        form_key="F1",
                    ),
                    UATVariableSpec(
                        variable_name="F",
                        variable_key="V2",
                        variable_type="Float",
                        form_key="F1",
                    ),
                    UATVariableSpec(
                        variable_name="D",
                        variable_key="V3",
                        variable_type="Date",
                        form_key="F1",
                    ),
                    UATVariableSpec(
                        variable_name="DT",
                        variable_key="V4",
                        variable_type="DateTime",
                        form_key="F1",
                    ),
                    UATVariableSpec(
                        variable_name="B",
                        variable_key="V5",
                        variable_type="Boolean",
                        form_key="F1",
                    ),
                    UATVariableSpec(
                        variable_name="CB",
                        variable_key="V6",
                        variable_type="Checkbox",
                        form_key="F1",
                        coded_values=["X", "Y"],
                    ),
                    UATVariableSpec(
                        variable_name="TA",
                        variable_key="V7",
                        variable_type="TextArea",
                        form_key="F1",
                    ),
                ],
            )
        ],
    )
    generator = SyntheticRecordGenerator(seed=42)
    results = generator.generate(spec, mock_snapshot)
    data = results[0].payloads[0]["data"]

    assert isinstance(data["N"], str)
    assert "." in data["F"]
    assert data["D"] == "2023-01-01"
    assert "T" in data["DT"]
    assert data["B"] in ("Yes", "No")
    assert any(c in data["CB"] for c in ("X", "Y"))
    assert len(data["TA"]) > 0


def test_subject_pool_logic(mock_snapshot):
    """Test subject pooling and wrap-around logic."""
    spec = UATSpecification(
        study_key="S1",
        study_name="S1",
        subject_specs=[
            UATSubjectSpec(site_name="S1", subject_count=3, subject_key_prefix="TEST-")
        ],
        form_specs=[
            UATFormSpec(
                form_key="F1",
                form_name="F1",
                form_type="Standard",
                test_type=RecordTestType.UPDATE_SCHEDULED_RECORD,
                subject_count=5,  # Should wrap around pool
                variables=[],
            )
        ],
    )
    generator = SyntheticRecordGenerator()
    results = generator.generate(spec, mock_snapshot)
    res = results[0]
    assert res.subject_keys == [
        "TEST-001",
        "TEST-002",
        "TEST-003",
        "TEST-001",
        "TEST-002",
    ]
    assert res.payloads[0]["subjectKey"] == "TEST-001"
    assert res.payloads[4]["subjectKey"] == "TEST-002"


def test_unrecognized_type(mock_snapshot, caplog):
    """Test handling of unrecognized variable types."""
    spec = UATSpecification(
        study_key="S1",
        study_name="S1",
        form_specs=[
            UATFormSpec(
                form_key="F1",
                form_name="F1",
                form_type="Standard",
                test_type=RecordTestType.CREATE_NEW_RECORD,
                subject_count=1,
                variables=[
                    UATVariableSpec(
                        variable_name="UNK",
                        variable_key="V1",
                        variable_type="UNKNOWN",
                        form_key="F1",
                    ),
                    UATVariableSpec(
                        variable_name="SIG",
                        variable_key="V2",
                        variable_type="Signature",
                        form_key="F1",
                    ),
                ],
            )
        ],
    )
    generator = SyntheticRecordGenerator()
    results = generator.generate(spec, mock_snapshot)
    assert "UNK" in results[0].payloads[0]["data"]
    assert results[0].payloads[0]["data"]["SIG"] == ""
    assert "Unrecognized variable type" in caplog.text


def test_no_subjects_pool_default(mock_snapshot):
    """Test default subject pool when none provided."""
    spec = UATSpecification(
        study_key="S1",
        study_name="S1",
        subject_specs=[],
        form_specs=[
            UATFormSpec(
                form_key="F1",
                form_name="F1",
                form_type="Standard",
                test_type=RecordTestType.CREATE_NEW_RECORD,
                subject_count=1,
                variables=[],
            )
        ],
    )
    generator = SyntheticRecordGenerator()
    results = generator.generate(spec, mock_snapshot)
    assert results[0].subject_keys == ["UAT-TEST-001"]
