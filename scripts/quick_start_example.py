from imednet import ImednetSDK, load_config_from_env
from imednet.utils import configure_json_logging

configure_json_logging()
cfg = load_config_from_env()
sdk = ImednetSDK(
    api_key=cfg.api_key,
    security_key=cfg.security_key,
    base_url=cfg.base_url,
)
print("SDK initialized successfully.")
