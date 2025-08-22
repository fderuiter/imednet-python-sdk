import pandas as pd
import pytest
from unittest.mock import MagicMock, patch

from imednet.sdk import ImednetSDK
from imednet.tlf.base import TlfReport


class ConcreteTestReport(TlfReport):
    def generate(self) -> pd.DataFrame:
        return pd.DataFrame({"col1": [1, 2], "col2": ["A", "B"]})


@pytest.fixture
def mock_sdk():
    return MagicMock(spec=ImednetSDK)


def test_tlf_report_init(mock_sdk):
    report = ConcreteTestReport(sdk=mock_sdk, study_key="test_study")
    assert report.sdk == mock_sdk
    assert report.study_key == "test_study"
    assert report.output_file is None
    assert report.options == {}


def test_tlf_report_init_with_options(mock_sdk):
    options = {"option1": "value1"}
    report = ConcreteTestReport(
        sdk=mock_sdk, study_key="test_study", output_file="test.csv", options=options
    )
    assert report.output_file == "test.csv"
    assert report.options == options


@patch("pandas.DataFrame.to_csv")
def test_save_to_file(mock_to_csv, mock_sdk):
    df = pd.DataFrame({"test": [1]})
    report = ConcreteTestReport(
        sdk=mock_sdk, study_key="test_study", output_file="test.csv"
    )
    report.save(df)
    mock_to_csv.assert_called_once_with("test.csv", index=False)


@patch("builtins.print")
def test_save_to_console(mock_print, mock_sdk):
    df = pd.DataFrame({"test": [1]})
    report = ConcreteTestReport(sdk=mock_sdk, study_key="test_study")
    report.save(df)
    mock_print.assert_called_with(df.to_string())


@patch.object(ConcreteTestReport, "generate", return_value=pd.DataFrame({"test": [1]}))
@patch.object(ConcreteTestReport, "save")
def test_run(mock_save, mock_generate, mock_sdk):
    report = ConcreteTestReport(sdk=mock_sdk, study_key="test_study")
    report.run()
    mock_generate.assert_called_once()
    mock_save.assert_called_once_with(mock_generate.return_value)
