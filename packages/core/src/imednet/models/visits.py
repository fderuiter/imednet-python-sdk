"""Models for subject visits and study events."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

from msgspec import field as Field

from imednet.models.engine import ModelEngine
from imednet.models.json_base import JsonModel


class Visit(JsonModel, kw_only=True, omit_defaults=True):
    """A specific instance of a subject visiting a site (or equivalent event)."""



Visit = ModelEngine.get_model('Visit', Visit)
