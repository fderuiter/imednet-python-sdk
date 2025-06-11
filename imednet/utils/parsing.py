from __future__ import annotations

from typing import Any, List

from ..models.base import Envelope
from ..models.records import Record
from ..models.sites import Site
from ..models.studies import Study


def parse_studies(json_obj: dict[str, Any]) -> List[Study]:
    """Parse a studies API response."""
    return Envelope[Study].model_validate(json_obj).data


def parse_sites(json_obj: dict[str, Any]) -> List[Site]:
    """Parse a sites API response."""
    return Envelope[Site].model_validate(json_obj).data


def parse_records(json_obj: dict[str, Any]) -> List[Record]:
    """Parse a records API response."""
    return Envelope[Record].model_validate(json_obj).data
