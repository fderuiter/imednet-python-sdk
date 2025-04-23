import os
from pathlib import Path

from dotenv import load_dotenv

from imednet.sdk import ImednetSDK
from imednet.workflows.record_mapper import RecordMapper

# Construct the path to the .env file in the project root
project_root = Path(__file__).resolve().parents[2]  # Go up two levels from workflows/ to the root
dotenv_path = project_root / ".env"

# Load environment variables from .env file, overriding existing ones
load_dotenv(dotenv_path=dotenv_path, override=True)

# 1. Pull your credentials from the environment
api_key: str = os.getenv("IMEDNET_API_KEY") or ""
security_key: str = os.getenv("IMEDNET_SECURITY_KEY") or ""
base_url: str = os.getenv("IMEDNET_BASE_URL") or ""

# 2. Initialize the SDK (this is where your keys go in)
sdk = ImednetSDK(
    api_key=api_key,
    security_key=security_key,
    base_url=base_url,
)

# 3. Instantiate the mapper
mapper = RecordMapper(sdk=sdk)

# 4. Fetch a DataFrame and print some diagnostics
df = mapper.dataframe(study_key="XXX", visit_key=None)

print(f"→ Retrieved DataFrame with shape: {df.shape}")
print(df.head(5))
