"""Workflow for pushing data to Veeva Vault."""

from __future__ import annotations

import asyncio
from typing import (
    Any,
    AsyncIterable,
    AsyncIterator,
    Iterable,
    List,
    Mapping,
    MutableMapping,
    Sequence,
)

from ..veeva import AsyncVeevaVaultClient, VeevaVaultClient, validate_record_for_upsert


async def _async_iter(
    iterable: AsyncIterable[MutableMapping[str, Any]] | Iterable[MutableMapping[str, Any]]
) -> AsyncIterator[MutableMapping[str, Any]]:
    """Yield items from an async or regular iterable uniformly."""
    if isinstance(iterable, AsyncIterable):
        async for item in iterable:
            yield item
    else:
        for item in iterable:
            yield item


class VeevaPushWorkflow:
    """Push iMednet record data to Veeva Vault objects."""

    def __init__(self, client: VeevaVaultClient) -> None:
        self._client = client

    def push_record(
        self,
        object_name: str,
        record: MutableMapping[str, Any],
        *,
        object_type: str | None = None,
        attachment_fields: Sequence[str] | None = None,
    ) -> MutableMapping[str, Any]:
        """Validate and upsert a single record."""
        if attachment_fields:
            for field in attachment_fields:
                if field in record:
                    record[field] = self._client.upload_attachment(str(record[field]))
        validated = validate_record_for_upsert(self._client, object_name, record, object_type)
        return self._client.upsert_object(object_name, validated)

    def push_records(
        self,
        object_name: str,
        records: Iterable[MutableMapping[str, Any]],
        *,
        object_type: str | None = None,
        attachment_fields: Sequence[str] | None = None,
    ) -> List[Mapping[str, Any]]:
        """Validate and upsert multiple records."""
        results: List[Mapping[str, Any]] = []
        for record in records:
            results.append(
                self.push_record(
                    object_name,
                    record,
                    object_type=object_type,
                    attachment_fields=attachment_fields,
                )
            )
        return results

    def push_records_bulk(
        self,
        object_name: str,
        records: Iterable[MutableMapping[str, Any]],
        *,
        object_type: str | None = None,
        id_param: str | None = None,
        migration_mode: bool = False,
        no_triggers: bool = False,
        batch_size: int = 500,
        attachment_fields: Sequence[str] | None = None,
    ) -> List[Mapping[str, Any]]:
        """Validate and upsert multiple records in batches."""
        prepared_batches: List[List[MutableMapping[str, Any]]] = [[]]
        for record in records:
            if attachment_fields:
                for field in attachment_fields:
                    if field in record:
                        record[field] = self._client.upload_attachment(str(record[field]))
            prepared_record = validate_record_for_upsert(
                self._client, object_name, record, object_type
            )
            batch = prepared_batches[-1]
            if len(batch) >= batch_size:
                prepared_batches.append([])
                batch = prepared_batches[-1]
            batch.append(prepared_record)

        results: List[Mapping[str, Any]] = []
        for batch in prepared_batches:
            if not batch:
                continue
            results.extend(
                self._client.bulk_upsert_objects(
                    object_name,
                    batch,
                    id_param=id_param,
                    migration_mode=migration_mode,
                    no_triggers=no_triggers,
                )
            )
        return results


class AsyncVeevaPushWorkflow:
    """Asynchronous variant of :class:`VeevaPushWorkflow`."""

    def __init__(self, client: AsyncVeevaVaultClient, *, concurrency: int = 5) -> None:
        self._client = client
        self._sem = asyncio.Semaphore(concurrency)

    async def push_record(
        self,
        object_name: str,
        record: MutableMapping[str, Any],
        *,
        object_type: str | None = None,
        attachment_fields: Sequence[str] | None = None,
    ) -> Mapping[str, Any]:
        """Validate and upsert a single record asynchronously."""
        if attachment_fields:
            for field in attachment_fields:
                if field in record:
                    record[field] = await self._client.upload_attachment(str(record[field]))
        validated = validate_record_for_upsert(self._client, object_name, record, object_type)
        results = await self._client.bulk_upsert_objects(object_name, [validated])
        return results[0]

    async def push_records(
        self,
        object_name: str,
        records: AsyncIterable[MutableMapping[str, Any]] | Iterable[MutableMapping[str, Any]],
        *,
        object_type: str | None = None,
        attachment_fields: Sequence[str] | None = None,
    ) -> List[Mapping[str, Any]]:
        """Validate and upsert multiple records asynchronously."""
        prepared: List[MutableMapping[str, Any]] = []
        async for record in _async_iter(records):
            if attachment_fields:
                for field in attachment_fields:
                    if field in record:
                        record[field] = await self._client.upload_attachment(str(record[field]))
            prepared.append(
                validate_record_for_upsert(self._client, object_name, record, object_type)
            )
        return await self._client.bulk_upsert_objects(object_name, prepared)

    async def push_records_bulk(
        self,
        object_name: str,
        records: AsyncIterable[MutableMapping[str, Any]] | Iterable[MutableMapping[str, Any]],
        *,
        object_type: str | None = None,
        id_param: str | None = None,
        migration_mode: bool = False,
        no_triggers: bool = False,
        batch_size: int = 500,
        attachment_fields: Sequence[str] | None = None,
    ) -> List[Mapping[str, Any]]:
        """Validate and upsert multiple records asynchronously in batches."""
        batches: List[List[MutableMapping[str, Any]]] = [[]]
        async for record in _async_iter(records):
            if attachment_fields:
                for field in attachment_fields:
                    if field in record:
                        record[field] = await self._client.upload_attachment(str(record[field]))
            prepared = validate_record_for_upsert(self._client, object_name, record, object_type)
            batch = batches[-1]
            if len(batch) >= batch_size:
                batches.append([])
                batch = batches[-1]
            batch.append(prepared)

        async def upsert(batch: List[MutableMapping[str, Any]]) -> List[Mapping[str, Any]]:
            async with self._sem:
                return await self._client.bulk_upsert_objects(
                    object_name,
                    batch,
                    id_param=id_param,
                    migration_mode=migration_mode,
                    no_triggers=no_triggers,
                )

        tasks = [asyncio.create_task(upsert(b)) for b in batches if b]
        results: List[Mapping[str, Any]] = []
        for t in tasks:
            results.extend(await t)
        return results
