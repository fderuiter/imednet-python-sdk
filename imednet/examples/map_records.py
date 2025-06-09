import os

from imednet.sdk import ImednetSDK
from imednet.workflows.record_mapper import RecordMapper

"""Example for converting study records to a pandas DataFrame using
:class:`RecordMapper`.

The script fetches all records for the configured study and prints the first few
rows of the resulting DataFrame. Set ``IMEDNET_VISIT_KEY`` to limit the records
to a specific visit.
"""

api_key = os.getenv("IMEDNET_API_KEY")
security_key = os.getenv("IMEDNET_SECURITY_KEY")
base_url = os.getenv("IMEDNET_BASE_URL")
study_key = os.getenv("IMEDNET_STUDY_KEY", "your_study_key_here")
visit_key = os.getenv("IMEDNET_VISIT_KEY")

if not api_key or not security_key:
    raise RuntimeError(
        "IMEDNET_API_KEY and IMEDNET_SECURITY_KEY environment variables must be set."
    )

sdk = ImednetSDK(api_key=api_key, security_key=security_key, base_url=base_url)
mapper = RecordMapper(sdk)

try:
    df = mapper.dataframe(study_key, visit_key=visit_key)
    print(df.head())
except Exception as e:
    print(f"Error mapping records: {e}")
