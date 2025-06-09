"""Workflow for incremental synchronization of iMednet records."""

from __future__ import annotations

import json
import os
from typing import TYPE_CHECKING, List, Optional, Set

from ..models import Record
from ..utils.filters import build_filter_string

if TYPE_CHECKING:  # pragma: no cover - used for type hints only
    from ..sdk import ImednetSDK


class IncrementalSyncWorkflow:
    """Synchronize newly created or updated records since the last run.

    Parameters
    ----------
    sdk:
        The :class:`~imednet.sdk.ImednetSDK` instance to use for API calls.
    state_file:
        Path to the JSON file used for storing the timestamp of the last
        successful sync.
    """

    def __init__(self, sdk: "ImednetSDK", state_file: str) -> None:
        self._sdk = sdk
        self._state_file = state_file

    # -----------------------------
    # State persistence helpers
    # -----------------------------
    def _read_state(self) -> Optional[str]:
        if not os.path.exists(self._state_file):
            return None
        try:
            with open(self._state_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            return data.get("last_sync")
        except Exception:
            return None

    def _write_state(self, timestamp: str) -> None:
        with open(self._state_file, "w", encoding="utf-8") as f:
            json.dump({"last_sync": timestamp}, f)

    # -----------------------------
    # Public API
    # -----------------------------
    def sync(self, study_key: str) -> List[Record]:
        """Fetch new/updated records since the last sync."""
        last_sync = self._read_state()
        filter_str = None
        if last_sync:
            filter_str = build_filter_string({"dateCreated": (">", last_sync)})

        revisions = self._sdk.record_revisions.list(study_key, filter=filter_str)
        if not revisions:
            return []

        record_ids: Set[int] = {rev.record_id for rev in revisions}
        records: List[Record] = [self._sdk.records.get(study_key, rid) for rid in record_ids]

        # Update state with latest timestamp
        latest = max(rev.date_created for rev in revisions)
        self._write_state(latest.isoformat())

        return records
