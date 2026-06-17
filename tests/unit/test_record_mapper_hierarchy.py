from datetime import datetime
from unittest.mock import MagicMock, patch

from imednet.models.records import Record
from imednet.models.variables import Variable
from imednet_workflows.record_mapper import RecordMapper


@patch("imednet_workflows.study_structure.get_study_structure")
def test_build_hierarchy(mock_get_study_structure):
    sdk = MagicMock()
    
    mock_study_struct = MagicMock()
    interval = MagicMock()
    form = MagicMock()
    form.form_id = 10
    var1 = Variable(variable_name="VAR1", label="Label1", form_id=10)
    var2 = Variable(variable_name="VAR2", label="Label2", form_id=10)
    form.variables = [var1, var2]
    interval.forms = [form]
    mock_study_struct.intervals = [interval]
    mock_get_study_structure.return_value = mock_study_struct
    
    records = [
        Record(
            record_id=1,
            subject_key="S1",
            visit_id=1,
            form_id=10,
            record_status="Complete",
            date_created=datetime(2021, 1, 1),
            record_data={"VAR1": "a", "VAR2": "b"},
        ),
        Record(
            record_id=2,
            subject_key="S1",
            visit_id=2,
            form_id=10,
            record_status="Complete",
            date_created=datetime(2021, 1, 2),
            record_data={"VAR1": "c", "VAR2": "d"},
            parent_record_id=999
        )
    ]
    
    mapper = RecordMapper(sdk)
    mapper._iter_records = MagicMock(return_value=records)
    
    # Run build_hierarchy with use_labels_as_keys = True
    tree = mapper.build_hierarchy("STUDY", use_labels_as_keys=True)
    
    assert len(tree) == 1
    subj = tree[0]
    assert subj["subject_key"] == "S1"
    assert len(subj["visits"]) == 2
    
    v1 = subj["visits"][0]
    assert v1["visit_id"] == 1
    assert len(v1["forms"]) == 1
    
    f10 = v1["forms"][0]
    assert f10["form_id"] == 10
    assert len(f10["records"]) == 1
    rec1 = f10["records"][0]
    assert rec1["Label1"] == "a"
    assert rec1["Label2"] == "b"
    assert rec1["parent_record_id"] == "1_10"
    
    v2 = subj["visits"][1]
    f10_2 = v2["forms"][0]
    rec2 = f10_2["records"][0]
    assert rec2["Label1"] == "c"
    assert rec2["Label2"] == "d"
    assert rec2["parent_record_id"] == 999

