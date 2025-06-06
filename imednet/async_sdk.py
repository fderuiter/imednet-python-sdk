"""Asynchronous SDK entry point."""

from __future__ import annotations

from typing import Optional

from .core.async_client import AsyncClient
from .core.context import Context
from .endpoints.async_codings import AsyncCodingsEndpoint
from .endpoints.async_forms import AsyncFormsEndpoint
from .endpoints.async_intervals import AsyncIntervalsEndpoint
from .endpoints.async_jobs import AsyncJobsEndpoint
from .endpoints.async_queries import AsyncQueriesEndpoint
from .endpoints.async_record_revisions import AsyncRecordRevisionsEndpoint
from .endpoints.async_records import AsyncRecordsEndpoint
from .endpoints.async_sites import AsyncSitesEndpoint
from .endpoints.async_studies import AsyncStudiesEndpoint
from .endpoints.async_subjects import AsyncSubjectsEndpoint
from .endpoints.async_users import AsyncUsersEndpoint
from .endpoints.async_variables import AsyncVariablesEndpoint
from .endpoints.async_visits import AsyncVisitsEndpoint


class AsyncImednetSDK:
    """Async variant of :class:`imednet.sdk.ImednetSDK`."""

    def __init__(
        self,
        api_key: str,
        security_key: str,
        base_url: Optional[str] = None,
        timeout: float = 30.0,
        retries: int = 3,
        backoff_factor: float = 1.0,
    ) -> None:
        self.ctx = Context()
        self._client = AsyncClient(
            api_key=api_key,
            security_key=security_key,
            base_url=base_url,
            timeout=timeout,
            retries=retries,
            backoff_factor=backoff_factor,
        )
        self.studies = AsyncStudiesEndpoint(self._client, self.ctx)
        self.forms = AsyncFormsEndpoint(self._client, self.ctx)
        self.sites = AsyncSitesEndpoint(self._client, self.ctx)
        self.subjects = AsyncSubjectsEndpoint(self._client, self.ctx)
        self.records = AsyncRecordsEndpoint(self._client, self.ctx)
        self.codings = AsyncCodingsEndpoint(self._client, self.ctx)
        self.intervals = AsyncIntervalsEndpoint(self._client, self.ctx)
        self.jobs = AsyncJobsEndpoint(self._client, self.ctx)
        self.queries = AsyncQueriesEndpoint(self._client, self.ctx)
        self.record_revisions = AsyncRecordRevisionsEndpoint(self._client, self.ctx)
        self.users = AsyncUsersEndpoint(self._client, self.ctx)
        self.variables = AsyncVariablesEndpoint(self._client, self.ctx)
        self.visits = AsyncVisitsEndpoint(self._client, self.ctx)

    async def __aenter__(self) -> "AsyncImednetSDK":
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: object | None,
    ) -> None:
        await self.aclose()

    async def aclose(self) -> None:
        await self._client.aclose()
