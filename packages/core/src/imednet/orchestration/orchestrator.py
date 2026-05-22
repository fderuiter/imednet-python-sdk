"""MultiStudyOrchestrator: concurrent multi-study pipeline engine."""

from __future__ import annotations

import logging
from typing import Any, Optional

from imednet.errors.orchestration import FilterConflictError

logger = logging.getLogger(__name__)


class MultiStudyOrchestrator:
    """Orchestrates pipeline execution across multiple active clinical trial boundaries.

    The SDK instance passed at construction is treated as an **immutable read-only
    resource** — no worker thread may mutate its transport, authentication state,
    or connection pool during parallel execution.

    Args:
        sdk: A fully initialized :class:`~imednet.ImednetSDK` instance. The
             orchestrator stores a reference (not a copy) and treats it as immutable.
        max_workers: Maximum number of concurrent worker threads. Defaults to 4.
             Set to 1 to force sequential execution (useful for debugging).

    Example::

        with ImednetSDK(api_key=..., security_key=...) as sdk:
            orchestrator = MultiStudyOrchestrator(sdk, max_workers=8)
            results = orchestrator.execute_pipeline(my_pipeline_func)
    """

    def __init__(self, sdk: Any, max_workers: int = 4) -> None:
        if max_workers < 1:
            raise ValueError(f"max_workers must be >= 1, got {max_workers}")
        self._sdk = sdk
        self._max_workers = max_workers

    @property
    def sdk(self) -> Any:
        """The shared read-only SDK instance."""
        return self._sdk

    @property
    def max_workers(self) -> int:
        """Maximum number of concurrent worker threads."""
        return self._max_workers

    def resolve_active_studies(
        self,
        whitelist: Optional[set[str]] = None,
        blacklist: Optional[set[str]] = None,
    ) -> list[str]:
        """Query the iMednet registry and apply filter matrices.

        Calls ``self._sdk.studies.list()`` to fetch the live study inventory,
        then applies the whitelist OR blacklist (mutually exclusive).

        Args:
            whitelist: If provided, only studies whose ``studyKey`` is in this
                       set are included. Mutually exclusive with ``blacklist``.
            blacklist: If provided, studies whose ``studyKey`` is in this set
                       are excluded. Mutually exclusive with ``whitelist``.

        Returns:
            Ordered list of study key strings targeting this execution run.

        Raises:
            FilterConflictError: When both ``whitelist`` and ``blacklist`` are
                non-empty simultaneously.
        """
        if whitelist and blacklist:
            raise FilterConflictError(whitelist=whitelist, blacklist=blacklist)

        all_studies = [study.study_key for study in self._sdk.studies.list()]
        logger.debug("Resolved %d studies from registry.", len(all_studies))

        if whitelist:
            filtered = [study_key for study_key in all_studies if study_key in whitelist]
            logger.info(
                "Whitelist filter applied: %d/%d studies selected.",
                len(filtered),
                len(all_studies),
            )
            return filtered

        if blacklist:
            filtered = [study_key for study_key in all_studies if study_key not in blacklist]
            logger.info(
                "Blacklist filter applied: %d/%d studies selected.",
                len(filtered),
                len(all_studies),
            )
            return filtered

        return all_studies


__all__ = ["MultiStudyOrchestrator"]
