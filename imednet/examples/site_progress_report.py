import os

from imednet.sdk import ImednetSDK
from imednet.workflows.site_progress import SiteProgressWorkflow

"""Generate a progress summary for all sites in a study using
:class:`SiteProgressWorkflow`. The script prints metrics such as subjects
enrolled, visits completed, and open queries per site.
"""

api_key = os.getenv("IMEDNET_API_KEY")
security_key = os.getenv("IMEDNET_SECURITY_KEY")
base_url = os.getenv("IMEDNET_BASE_URL")
study_key = os.getenv("IMEDNET_STUDY_KEY", "your_study_key_here")

if not api_key or not security_key:
    raise RuntimeError(
        "IMEDNET_API_KEY and IMEDNET_SECURITY_KEY environment variables must be set."
    )

sdk = ImednetSDK(api_key=api_key, security_key=security_key, base_url=base_url)
workflow = SiteProgressWorkflow(sdk)

try:
    progress = workflow.get_site_progress(study_key)
    for site in progress:
        print(site.model_dump())
except Exception as e:
    print(f"Error retrieving site progress: {e}")
