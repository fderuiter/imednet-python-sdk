"""Lightweight client for the iMednet v2 API."""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, cast

import requests
from pydantic import BaseModel


class MednetApiError(Exception):
    """Raised when the iMednet API returns an error."""


class Form(BaseModel):
    """Simplified form representation."""

    id: int
    name: str


class Variable(BaseModel):
    """Simplified variable representation."""

    id: int
    name: str


class MednetClient:
    """Simple wrapper around the iMednet REST API."""

    BASE_URL = "https://api.imednet.com/v2"

    def __init__(self, study_key: str, headers: Dict[str, str]) -> None:
        self.study_key = study_key
        self.headers = headers

    def _request(self, path: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Internal GET request with basic retry and back-off."""
        url = f"{self.BASE_URL}{path}"
        backoff = 1
        for attempt in range(3):
            try:
                resp = requests.get(url, headers=self.headers, params=params, timeout=10)
            except requests.RequestException as exc:
                if attempt == 2:
                    raise MednetApiError(str(exc)) from exc
            else:
                if resp.status_code == 200:
                    return cast(Dict[str, Any], resp.json())
                if 500 <= resp.status_code < 600 and attempt < 2:
                    pass
                else:
                    raise MednetApiError(f"HTTP {resp.status_code}: {resp.text}")
            time.sleep(backoff)
            backoff *= 2
        raise MednetApiError("Max retries exceeded")

    def get_forms(self, test_mode: bool = False) -> List[Form]:
        """Return list of forms for the configured study."""
        if test_mode:
            fixture = (
                Path(__file__).resolve().parents[1] / "tests" / "fixtures" / "mednet_sample.json"
            )
            with fixture.open("r", encoding="utf-8") as fh:
                data = json.load(fh)
        else:
            data = self._request(f"/studies/{self.study_key}/forms")
        forms = data.get("forms", data.get("data", []))
        return [Form.model_validate(f) for f in forms]

    def get_variables(self, form_id: int) -> List[Variable]:
        """Return variables for a form, handling pagination."""
        path = f"/forms/{form_id}/variables"
        params: Optional[Dict[str, Any]] = None
        results: List[Variable] = []
        while True:
            data = self._request(path, params=params)
            vars_data = data.get("variables", data.get("data", []))
            results.extend(Variable.model_validate(v) for v in vars_data)
            token = data.get("nextPageToken")
            if not token:
                break
            params = {"pageToken": token}
        return results
