from abc import ABC, abstractmethod
from typing import Dict, Any
import pandas as pd

from imednet.sdk import ImednetSDK


class TlfDefinition(ABC):
    """Abstract base class for a TLF definition."""

    name: str
    title: str

    @abstractmethod
    def generate(self, sdk: ImednetSDK, study_id: str, **kwargs: Dict[str, Any]) -> pd.DataFrame:
        """
        Generate the data for the TLF.

        :param sdk: An instance of the ImednetSDK.
        :param study_id: The ID of the study to generate the TLF for.
        :param kwargs: Additional arguments for the TLF generation.
        :return: A pandas DataFrame containing the TLF data.
        """
        pass


class AdverseEventsListing(TlfDefinition):
    """A listing of all adverse events for a study."""

    name = "adverse_events"
    title = "Adverse Events Listing"

    def generate(self, sdk: ImednetSDK, study_id: str, **kwargs: Dict[str, Any]) -> pd.DataFrame:
        """
        Generate a listing of all adverse events.

        This is a simplified example and makes assumptions about the study structure.
        In a real-world scenario, the form key and variable names would likely
        be more dynamic or configurable.

        :param sdk: An instance of the ImednetSDK.
        :param study_id: The ID of the study to generate the TLF for.
        :param kwargs: Expects 'form_key' to identify the AE form. Defaults to 'AE'.
        :return: A pandas DataFrame containing the adverse events data.
        """
        ae_form_key = kwargs.get("form_key", "AE")

        all_records = sdk.records.list(study_id, form_key=ae_form_key)

        if not all_records:
            return pd.DataFrame()

        # The record data is in the 'record_data' attribute of each record.
        # We'll extract this data and create a DataFrame.
        ae_data = [record.record_data for record in all_records]

        df = pd.DataFrame(ae_data)

        # The column names will be the variable names from the AE form.
        # We can perform some basic cleanup or column selection here.
        # For example, let's assume some common AE variable names.
        ae_columns = [
            "SUBJECT_ID",  # Assuming this is a variable in the form
            "AETERM",
            "AESTARTDTC",
            "AEENDTC",
            "AESEV",
            "AEREL",
        ]

        # Filter the DataFrame to only include the columns that actually exist
        # in the fetched data to avoid errors.
        existing_columns = [col for col in ae_columns if col in df.columns]

        if not existing_columns:
            # If none of the expected columns are present, return the full dataframe
            # but this might indicate a configuration problem.
            return df

        return df[existing_columns]


# A registry of available TLF definitions
TLF_DEFINITIONS = {
    AdverseEventsListing.name: AdverseEventsListing,
}
