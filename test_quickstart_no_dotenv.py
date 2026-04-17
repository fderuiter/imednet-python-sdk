from imednet import ImednetSDK, load_config
from imednet.utils import configure_json_logging

configure_json_logging()
cfg = load_config()

with ImednetSDK(
    api_key=cfg.api_key,
    security_key=cfg.security_key,
    base_url=cfg.base_url,
) as sdk:
    studies = sdk.studies.list()
    for study in studies:
        print(f"{study.study_name} ({study.study_key})")
