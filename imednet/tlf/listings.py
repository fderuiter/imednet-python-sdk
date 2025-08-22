from typing import List

import pandas as pd

from imednet.models import Subject
from imednet.tlf.base import TlfReport


class SubjectListing(TlfReport):
    """
    A subject listing report.

    This report generates a listing of all subjects in a study, including their
    status, site, and enrollment date.
    """

    def generate(self) -> pd.DataFrame:
        """
        Generate the subject listing report.

        Returns:
            A pandas DataFrame containing the subject listing.
        """
        subjects: List[Subject] = list(self.sdk.subjects.list(study_key=self.study_key))

        if not subjects:
            return pd.DataFrame(
                columns=["Subject ID", "Status", "Site", "Enrollment Date"]
            )

        data = [
            {
                "Subject ID": s.subject_key,
                "Status": s.subject_status,
                "Site": s.site_name,
                "Enrollment Date": s.enrollment_start_date,
            }
            for s in subjects
        ]

        df = pd.DataFrame(data)
        return df
