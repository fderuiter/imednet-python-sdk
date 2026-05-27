"""Study metadata inspector for UAT specification generation."""

from __future__ import annotations

import asyncio
from datetime import datetime
from typing import TYPE_CHECKING, TypedDict, cast

from pydantic import Field

from imednet.models.base import ImednetBaseModel
from imednet.models.forms import Form
from imednet.models.intervals import Interval
from imednet.models.sites import Site
from imednet.models.variables import Variable

if TYPE_CHECKING:
    from imednet.sdk import AsyncImednetSDK, ImednetSDK


class FormVariableMap(TypedDict):
    form: Form
    variables: list[Variable]


class StudySnapshot(ImednetBaseModel):
    """Point-in-time snapshot of a study's structural metadata."""

    study_key: str
    captured_at: datetime = Field(default_factory=datetime.utcnow)
    forms: list[Form]
    variables: list[Variable]
    intervals: list[Interval]
    sites: list[Site]
    forms_by_key: dict[str, Form] = Field(default_factory=dict)
    variables_by_form: dict[str, list[Variable]] = Field(default_factory=dict)
    intervals_by_name: dict[str, Interval] = Field(default_factory=dict)

    def model_post_init(self, __context: object) -> None:
        self.forms_by_key = {form.form_key: form for form in self.forms}
        self.variables_by_form = {}
        for variable in self.variables:
            self.variables_by_form.setdefault(variable.form_key, []).append(variable)
        self.intervals_by_name = {interval.interval_name: interval for interval in self.intervals}

    def enrollment_forms(self) -> list[Form]:
        """Return forms with form_type indicating subject registration."""
        return [form for form in self.forms if form.form_type in ("Enrollment", "Registration")]

    def scheduled_forms(self) -> list[Form]:
        """Return scheduled (non-enrollment, non-unscheduled) forms."""
        return [
            form
            for form in self.forms
            if not form.unscheduled_visit and form.form_type not in ("Enrollment", "Registration")
        ]

    def unscheduled_forms(self) -> list[Form]:
        """Return unscheduled forms."""
        return [form for form in self.forms if form.unscheduled_visit]

    def active_sites(self) -> list[Site]:
        """Return sites that are actively enrolling."""
        return [site for site in self.sites if site.site_enrollment_status == "Active"]


class StudySchemaInspector:
    """Fetch and index all structural metadata for an iMednet study.

    Supports both sync and async SDK clients. When an async client is used,
    metadata calls are executed concurrently via ``asyncio.gather``.
    The in-memory cache is per inspector instance and is not thread-safe;
    use external synchronization or separate inspector instances for concurrent access.
    """

    def __init__(self, sdk: ImednetSDK | AsyncImednetSDK) -> None:
        self._sdk = sdk
        self._cache: dict[str, StudySnapshot] = {}

    def _ensure_sync_sdk(self) -> None:
        missing = [
            endpoint
            for endpoint in ("forms", "variables", "intervals", "sites")
            if not hasattr(getattr(self._sdk, endpoint, None), "list")
        ]
        if missing:
            raise TypeError(
                "inspect() requires a synchronous ImednetSDK with list() methods on "
                f"forms/variables/intervals/sites. Missing sync methods for: {', '.join(missing)}."
            )

    def _ensure_async_sdk(self) -> None:
        missing = [
            endpoint
            for endpoint in ("forms", "variables", "intervals", "sites")
            if not hasattr(getattr(self._sdk, endpoint, None), "async_list")
        ]
        if missing:
            raise TypeError(
                "async_inspect() requires an AsyncImednetSDK with async_list() methods on "
                f"forms/variables/intervals/sites. Missing async methods for: {', '.join(missing)}."
            )

    def inspect(self, study_key: str, *, force_refresh: bool = False) -> StudySnapshot:
        """Synchronously fetch and return a study snapshot."""
        self._ensure_sync_sdk()
        if not force_refresh and study_key in self._cache:
            return self._cache[study_key]

        sdk = cast("ImednetSDK", self._sdk)
        snapshot = StudySnapshot(
            study_key=study_key,
            forms=sdk.forms.list(study_key),
            variables=sdk.variables.list(study_key),
            intervals=sdk.intervals.list(study_key),
            sites=sdk.sites.list(study_key),
        )
        self._cache[study_key] = snapshot
        return snapshot

    async def async_inspect(self, study_key: str, *, force_refresh: bool = False) -> StudySnapshot:
        """Asynchronously fetch metadata concurrently and return a study snapshot."""
        self._ensure_async_sdk()
        if not force_refresh and study_key in self._cache:
            return self._cache[study_key]

        sdk = cast("AsyncImednetSDK", self._sdk)
        forms, variables, intervals, sites = await asyncio.gather(
            sdk.forms.async_list(study_key),
            sdk.variables.async_list(study_key),
            sdk.intervals.async_list(study_key),
            sdk.sites.async_list(study_key),
        )

        snapshot = StudySnapshot(
            study_key=study_key,
            forms=forms,
            variables=variables,
            intervals=intervals,
            sites=sites,
        )
        self._cache[study_key] = snapshot
        return snapshot

    def clear_cache(self, study_key: str | None = None) -> None:
        """Clear snapshot cache for one study key or all keys."""
        if study_key is None:
            self._cache.clear()
            return
        self._cache.pop(study_key, None)
