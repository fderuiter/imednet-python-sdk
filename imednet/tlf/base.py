from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

import pandas as pd

from imednet.sdk import ImednetSDK


class TlfReport(ABC):
    """Abstract base class for a TLF report."""

    def __init__(
        self,
        sdk: ImednetSDK,
        study_key: str,
        output_file: Optional[str] = None,
        options: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize the report.
        Args:
            sdk: An instance of the ImednetSDK.
            study_key: The key of the study to generate the report for.
            output_file: Optional. The path to save the report to.
            options: Optional. A dictionary of report-specific options.
        """
        self.sdk = sdk
        self.study_key = study_key
        self.output_file = output_file
        self.options = options or {}

    @abstractmethod
    def generate(self) -> pd.DataFrame:
        """
        Generate the report.
        This method should be implemented by subclasses to generate the specific
        TLF report.
        Returns:
            A pandas DataFrame containing the report data.
        """
        raise NotImplementedError

    def save(self, df: pd.DataFrame) -> None:
        """
        Save the report to a file.
        This method saves the generated DataFrame to a CSV file if an output
        file path is provided.
        Args:
            df: The DataFrame to save.
        """
        if self.output_file:
            df.to_csv(self.output_file, index=False)
            print(f"Report saved to {self.output_file}")
        else:
            print(df.to_string())

    def run(self) -> None:
        """
        Run the report generation and save the output.
        """
        df = self.generate()
        self.save(df)
