import os
from pathlib import Path

from dotenv import load_dotenv
from imednet.sdk import ImednetSDK as ImednetClient

# Construct the path to the .env file in the project root
project_root = Path(__file__).resolve().parents[2]  # Go up two levels from examples/ to the root
dotenv_path = project_root / ".env"

# Load environment variables from .env file, overriding existing ones
load_dotenv(dotenv_path=dotenv_path, override=True)

api_key = os.getenv("IMEDNET_API_KEY")
security_key = os.getenv("IMEDNET_SECURITY_KEY")
base_url = os.getenv("IMEDNET_BASE_URL")

try:
    client = ImednetClient(api_key=api_key, security_key=security_key, base_url=base_url)
    studies = client.studies.list()
    if not studies:
        print("No studies returned from API.")
    for study in studies[:1]:
        study_key = study.study_key
        subjects = client.subjects.list(study_key=study_key)
        print(f"Subjects for study '{study_key}': {len(subjects)}")
        for subject in subjects[:5]:
            print(f"- Subject Key: {subject.subject_key}, Status: {subject.subject_status}")
except Exception as e:
    print(f"Error: {e}")
