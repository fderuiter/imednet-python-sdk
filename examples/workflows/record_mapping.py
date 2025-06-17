import os

from imednet.sdk import ImednetSDK
from imednet.workflows.record_mapper import RecordMapper

"""Example script that saves study records to CSV using RecordMapper."""

api_key = os.getenv("IMEDNET_API_KEY", "XXXXXXXXXX")
security_key = os.getenv("IMEDNET_SECURITY_KEY", "XXXXXXXXXX")
base_url = os.getenv("IMEDNET_BASE_URL")
study_key = os.getenv("IMEDNET_STUDY_KEY", "XXXXXXXXXX")

output_path = os.path.join(os.path.dirname(__file__), "record_mapping_output", "records.csv")

try:
    sdk = ImednetSDK(api_key=api_key, security_key=security_key, base_url=base_url)
    mapper = RecordMapper(sdk)
    df = mapper.dataframe(study_key=study_key)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False)
    print(f"Saved {len(df)} records to {output_path}")
except Exception as e:
    print(f"Error mapping records: {e}")
