"""Job and background operation models for iMedNet."""

from __future__ import annotations

from typing import Any

from pydantic import Field, field_validator

from imednet.models.base import ImednetBaseModel

class Job(ImednetBaseModel):
    """Represents an asynchronous background job."""

    @property
    def is_terminal(self) -> bool:
        """Checks if the job has reached a final state (Success/Failed/Cancelled)."""
        return (
            self.state.upper() in {"COMPLETED", "SUCCESS", "FAILED", "CANCELLED"}
            if self.state
            else False
        )

    @property
    def is_successful(self) -> bool:
        """Checks if the job completed successfully."""
        return self.state.upper() in {"COMPLETED", "SUCCESS"} if self.state else False

    @property
    def is_failed(self) -> bool:
        """Checks if the job failed or was cancelled."""
        return self.state.upper() in {"FAILED", "CANCELLED"} if self.state else False

    job_id: str | None
    batch_id: str | None
    state: str | None
    date_created: Any
    date_finished: Any
    date_started: Any

class JobStatus(Job):
    """Extended job information returned when polling."""

    results: Any = Field(default=None)

    @field_validator("progress", mode="before", check_fields=False)  # type: ignore[untyped-decorator]
    def _parse_progress(cls, v: Any) -> int:
        """Parse progress value as an integer.

        Args:
            v: The progress value from the API.

        Returns:
            The parsed integer progress.
        """
        try:
            return int(v)
        except (TypeError, ValueError):
            return 0

    @property
    def total_records(self) -> int:
        """Return the total number of records processed."""
        if isinstance(self.results, list):
            return len(self.results)
        if isinstance(self.results, dict):
            return int(self.results.get("total", 0))
        if self.results:
            return 1
        return 0

    @property
    def successful_records(self) -> int:
        """Return the total number of successful records processed."""
        if isinstance(self.results, list):
            return sum(
                1
                for r in self.results
                if isinstance(r, dict)
                and (r.get("status") or "").upper() in {"PASS", "SUCCESS", "COMPLETED"}
            )
        if isinstance(self.results, dict):
            return int(self.results.get("success", 0))
        if self.is_successful and self.results:
            return 1
        return 0

    @property
    def failed_records(self) -> int:
        """Return the total number of failed records processed."""
        if isinstance(self.results, list):
            return sum(
                1
                for r in self.results
                if isinstance(r, dict)
                and (r.get("status") or "").upper() in {"FAIL", "FAILED", "ERROR"}
            )
        if isinstance(self.results, dict):
            return int(self.results.get("failed", 0))
        if self.is_failed and self.results:
            return 1
        # If it's plain text and state is failed, we count it as 1 failure.
        return 0

    job_id: str | None
    batch_id: str | None
    state: str | None
    date_created: str | None
    date_started: str | None
    date_finished: str | None
    progress: int | None
    result_url: str | None
