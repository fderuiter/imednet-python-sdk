from __future__ import annotations

import time
from typing import Any, Mapping

import requests

RETRY_STATUS = {429, 500, 502, 503, 504}
BASE_URL = "https://edc.prod.imednetapi.com/api/v1/edc"
USER_AGENT = "imednet-sdk/0.1"


class Client:
    """Thin HTTP wrapper with retry/back‑off."""

    def __init__(self, api_key: str, security_key: str, timeout: int = 30):
        self.api_key, self.security_key, self.timeout = api_key, security_key, timeout
        self.session = requests.Session()

    # ---- public verbs ----
    def get(self, path: str, **kwargs: Any) -> Any:
        return self._request("GET", path, **kwargs)

    # ---- internals ----
    def _headers(self) -> Mapping[str, str]:
        return {
            "x-api-key": self.api_key,
            "x-imn-security-key": self.security_key,
            "User-Agent": USER_AGENT,
            "Content-Type": "application/json",
        }

    def _request(self, method: str, path: str, **kwargs: Any) -> Any:
        url = f"{BASE_URL}{path}"
        retries = 0
        while True:
            resp = self.session.request(
                method, url, headers=self._headers(), timeout=self.timeout, **kwargs
            )
            if resp.status_code not in RETRY_STATUS or retries >= 3:
                break
            retries += 1
            time.sleep(0.5 * 2 ** (retries - 1))
        resp.raise_for_status()
        return resp.json()
