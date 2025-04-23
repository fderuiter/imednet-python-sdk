# iMednet Python SDK — Reference Implementation Guide

This document provides a comprehensive “blueprint to code” checklist for a Python SDK wrapper around the iMednet REST API, including corrections and clarifications based on the latest API reference.

---

## 0 Common Base

- **Base URL**: All endpoints live under:

  ```python
  BASE_URL = "https://edc.prod.imednetapi.com/api/v1/edc"
  ```

- **Study Scope**: Every collection (variables, records, sites, etc.) is nested under a specific study key: `/studies/{studyKey}/…`.
- **JSON shape**: All responses have the form:

  ```json
  {
    "data": [...],
    "pagination": { /* page info */ }
  }
  ```

  - Use `"data"` for payload items, and `"pagination"` for paging metadata.
- **Filtering**:
  - Standard filters go in the `filter` query param: attribute names are case-sensitive and joined by `;` (AND) or `,` (OR).

    ```http
    GET /studies/ABC/variables?filter=formId==123;visitKey==V1
    ```

  - Record‑data filters use a separate `recordDataFilter` param.

---

## 1 `imednet/core/` (Layer 0 – Transport & Plumbing)

| File             | Class / Callable         | Public API                              | Notes                                                                                 |
|------------------|--------------------------|-----------------------------------------|---------------------------------------------------------------------------------------|
| **client.py**    | `Client`                 | `get(path, params=None) -> dict`        | Joins `BASE_URL + path`, sends HTTP, returns full JSON payload (`data` + `pagination`).|
|                  |                          | `post(path, json=None) -> dict`         | Same shape as `get()` on `payload` return.                                            |
|                  |                          | `paginate(path, params=None) -> Iterator[dict]` | Loops pages, yields each item in response[`data`].                            |
|                  | `AuthorizedSession` *(opt)* | —                                    | Hook for OAuth device‑code or token‑refresh logic.                                     |
| **paginator.py** | `Paginator`              | `iterate(path, params=None, page_key="data") -> Generator[dict]` | Encapsulates `page`/`pageSize` looping; used by `Client.paginate()`.                   |
| **context.py**   | `Context`                | Attributes: `study_key`, `sponsor_key`;`use_study(studyKey)` context manager | Holds mutable config shared across endpoints.                                        |
| **exceptions.py**| `ImednetError` (base)`HTTPError`, `Unauthorized`, `NotFound`, `TooManyRequests`, `ServerError` | —         | `Client._handle_response` maps status codes → these exceptions.                         |
| **filters.py**   | `build(filter_dict: dict) -> str` | —                             | Converts `{"formId":123,"visitKey":"V1"}` → `formId==123;visitKey==V1`.           |
| **logging.py**   | `get_logger(name) -> logging.Logger` | —                       | Centralises formatting so host app can configure log capture.                         |

---

## 2 `imednet/utils/` (Layer 1 – Pure Helpers)

| File          | Purpose                        | Representative Functions                              |
|---------------|--------------------------------|-------------------------------------------------------|
| **dates.py**  | ISO ↔ `datetime` conversion     | `to_iso(dt: datetime) -> str``parse_iso(s: str) -> datetime``now_iso() -> str` |
| **typing.py** | Common type aliases            | `JSON = dict[str, Any]``DF = pandas.DataFrame`     |
| **export.py** | Light wrappers around Pandas I/O | `to_parquet(df: DF, path: Path)``zip_dir(dir: Path)` |
| **retry.py**  | Backoff decorator (opt)         | `@backoff(max_tries: int, factor: float)`              |

---

## 3 `imednet/models/` (Layer 2 – Schema)

Define one `@dataclass` per resource, matching JSON keys exactly. All expose:

```python
@classmethod
from_json(cls, raw: JSON) -> "Model"
```

| Model        | Fields (JSON keys)                           |
|--------------|----------------------------------------------|
| **Study**    | `studyKey`, `studyId`, `studyName`, `studyType`, … |
| **Variable** | `variableKey`, `variableId`, `formId`, `visitKey`, `label`, `dataType`, … |
| **Record**   | `recordKey`, `subjectKey`, `formId`, `visitKey`, `values: dict`, `status`, `tsCreated`, … |
| **Site**     | `siteId`, `siteName`, `country`, `status`, … |
| **Query**    | `annotationId`, `subjectKey`, `field`, `state`, `raisedBy`, `createdTs`, … |
| **Subject**  | `subjectKey`, `subjectId`, `randomizationKey`, … |
| **Visit**    | `visitKey`, `visitId`, `visitName`, `scheduledDate`, … |
| **RecordRevision** | `revisionId`, `recordKey`, `changes`, `timestamp`, … |
| **Coding**   | `codingId`, `code`, `description`, …         |
| **Job**      | `batchId`, `status`, `submittedTs`, …        |

---

## 4 `imednet/endpoints/` (Layer 3 – Thin Wrappers)

### BaseEndpoint mix‑in

```python
class BaseEndpoint:
    def __init__(self, client: Client, ctx: Context):
        self._client = client
        self._ctx = ctx
        self.base = f"/studies/{ctx.study_key}"

    def _auto_filter(self, kwargs: dict) -> dict:
        # Inject studyKey if not provided
        if "studyKey" not in kwargs:
            kwargs["studyKey"] = self._ctx.study_key
        return kwargs
```

### Resource Endpoints

| File              | Class                 | Paths (GET)                                                                      |
|-------------------|-----------------------|----------------------------------------------------------------------------------|
| **study.py**      | `StudyEndpoint`       | `GET /studies``GET /studies/{studyKey}`                                      |
| **variable.py**   | `VariableEndpoint`    | `GET {base}/variables``GET {base}/variables?filter=…`                         |
| **record.py**     | `RecordEndpoint`      | `GET {base}/records``POST {base}/records` (batch create)`GET {base}/jobs/{batchId}` status |
| **site.py**       | `SiteEndpoint`        | `GET {base}/sites``GET {base}/sites/{siteId}`                                 |
| **query.py**      | `QueryEndpoint`       | `GET {base}/queries?filter=annotationId==…`(no single-item `/queries/{id}`)   |
| **subject.py**    | `SubjectEndpoint`     | `GET {base}/subjects``GET {base}/subjects/{subjectKey}`                       |
| **visit.py**      | `VisitEndpoint`       | `GET {base}/visits``GET {base}/visits/{visitKey}`                             |
| **revision.py**   | `RecordRevisionEndpoint` | `GET {base}/recordRevisions`                                                  |
| **coding.py**     | `CodingEndpoint`      | `GET {base}/codings`                                                             |
| **job.py**        | `JobEndpoint`         | `GET {base}/jobs/{batchId}`                                                      |

**Implementation pattern** (e.g. `StudyEndpoint.list`):

```python
def list(self, **filters) -> list[Model]:
    params = {"filter": build(self._auto_filter(filters))}
    raw_items = self._client.paginate(f"/studies/{self._ctx.study_key}/studies", params=params)
    return [Study.from_json(item) for item in raw_items]
```

---

## 5 `imednet/workflows/` (Layer 4 – Power‑user Recipes)

These higher‑level recipes compose one or more endpoints into Pandas DataFrames or directory exports:

| Module               | Class / Func                                      | Signature                                                           |
|----------------------|---------------------------------------------------|---------------------------------------------------------------------|
| **record_mapper.py** | `RecordMapper`                                    | `dataframe(study_key, form_id, visit_key=None) -> DF`              |
| **export_bundle.py** | `export(study_key, out_dir, parquet=False) -> Path` | Exports all records, variables, queries, etc. in one folder         |
| **crf_progress.py**  | `progress(study_key) -> DF`                       | Shows CRF completion status                                         |
| **query_log.py**     | `history(study_key, unresolved_only=False) -> DF` | Lists query audit trail                                             |
| **snapshot_diff.py** | `diff(old_dir, new_dir) -> DF`                    | Compares two export bundles                                        |

Each accepts endpoint instances in `__init__`, enabling stub‑based testing.

---

## 6 `imednet/sdk.py` — Façade Wiring

```python
class ImednetSDK:
    def __init__(self, api_key: str, security_key: str):
        self.ctx = Context()
        client = Client(api_key, security_key)
        # Endpoints
        self.studies   = StudyEndpoint(client, self.ctx)
        self.variables = VariableEndpoint(client, self.ctx)
        self.records   = RecordEndpoint(client, self.ctx)
        self.sites     = SiteEndpoint(client, self.ctx)
        self.queries   = QueryEndpoint(client, self.ctx)
        self.subjects  = SubjectEndpoint(client, self.ctx)
        self.visits    = VisitEndpoint(client, self.ctx)
        self.revisions = RecordRevisionEndpoint(client, self.ctx)
        self.codings   = CodingEndpoint(client, self.ctx)
        self.jobs      = JobEndpoint(client, self.ctx)
        # Workflows
        self.workflow = types.SimpleNamespace(
            record_mapper = RecordMapper(self.variables, self.records),
            export_bundle = export_bundle,
            crf_progress  = crf_progress,
            query_log     = query_log,
            snapshot_diff = snapshot_diff,
        )
```

---

## 7 `imednet/cli.py` (Typer-based CLI)

| Command         | Calls                                           | Flags                                      |
|-----------------|------------------------------------------------|-------------------------------------------|
| `imed studies`  | `sdk.studies.list()`                           | `--filter "studyKey==XYZ"`                |
| `imed variables`| `sdk.variables.list()`                         | `--filter "variableKey==…"`               |
| `imed records`  | `sdk.records.list()` and/or `sdk.records.create()` | `--filter`, `--file batch.json`        |
| `imed sites`    | `sdk.sites.list()`                             |                                           |
| `imed queries`  | `sdk.queries.list()`                           | `--state open\|closed`                     |
| `imed mapper`   | `sdk.workflow.record_mapper.dataframe()`       | `--study`, `--form`, `--visit`, `--out csv`|
| `imed export`   | `sdk.workflow.export_bundle.export()`          | `--study`, `--dir`, `--parquet`           |

---

## 8 `tests/` Roadmap

1. **Unit/core** — mock `requests.Session.request` via `responses`, test `Client`, `Paginator`, filters, exceptions.
2. **Endpoint contracts** — fixture JSON, assert `Model.from_json` yields correct dataclasses.
3. **Workflow snapshots** — `assert_frame_equal` vs stored Parquet/CSV snapshots.
4. **Integration** — nightly sandbox run against `/studies`, `/variables`; alert on schema changes.

---

## Implementation Order Suggestion

1. **Core modules** (`exceptions`, `paginator`, `client`) + unit tests.
2. **Endpoints** one by one (adding model fields as needed).
3. **RecordMapper** workflow to unlock early value.
4. **Remaining utils** (`dates`, `export`, `retry`).
5. **CLI** once APIs and models stabilize.

With this updated checklist—including corrected base URL, nested study paths, unified JSON handling, full endpoint coverage, and precise filtering—you have a turnkey roadmap to deliver a fully‑featured, well‑tested iMednet Python SDK.
