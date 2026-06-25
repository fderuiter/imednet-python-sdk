"""Record Mapper module."""

from __future__ import annotations

import logging
from collections.abc import Iterable, Iterator
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Tuple, Type, Union

try:
    import pandas as pd
except ImportError:
    pd = None  # type: ignore
from pydantic import BaseModel, Field, ValidationError, create_model

from imednet.spi.endpoints import Record as RecordModel  # type: ignore[attr-defined]
from imednet.spi.endpoints import Variable as VariableModel  # type: ignore[attr-defined]

from .cached_loader import CachedRecordsLoader
from .chunked_pipeline import DEFAULT_CHUNK_SIZE, ChunkedRecordPipeline, iter_chunks

if TYPE_CHECKING:
    from imednet.spi.facade import ImednetFacade

# Setup basic logging
logger = logging.getLogger(__name__)


class RecordMapper:
    """Maps EDC records for a study into a pandas DataFrame.

    Features:
      - Fetches variable definitions for column mapping.
      - Dynamically creates a Pydantic model for type validation of record data.
      - Fetches records, applying server-side filtering where possible.
      - Merges metadata and record data.
      - Offers choice between variable names or labels for column headers.
      - Handles parsing errors gracefully for individual records.

    Example:
        sdk = ImednetSDK(api_key, security_key, base_url)
        mapper = RecordMapper(sdk)
        # Get DataFrame with labels as columns, filtered by visit
        df_labels = mapper.dataframe(study_key="MYSTUDY", visit_key="VISIT1")
        # Get DataFrame with variable names as columns
        df_names = mapper.dataframe(study_key="MYSTUDY", use_labels_as_columns=False)
    """

    def __init__(
        self,
        sdk: "ImednetFacade",
        *,
        loader: CachedRecordsLoader | None = None,
        chunk_size: int = DEFAULT_CHUNK_SIZE,
    ) -> None:
        """Initialize with an :class:`ImednetSDK` instance.

        ``loader`` enables cache-backed streaming for large-study workflows.
        ``chunk_size`` controls the maximum number of records parsed into each
        yielded batch when using chunked mapping helpers.
        """
        self.sdk = sdk
        self._loader = loader
        self._pipeline = ChunkedRecordPipeline(chunk_size=chunk_size)

    # ------------------------------------------------------------------
    # Helper methods
    # ------------------------------------------------------------------
    def _fetch_variable_metadata(
        self,
        study_key: str,
        variable_whitelist: Optional[List[str]] = None,
        form_whitelist: Optional[List[int]] = None,
    ) -> Tuple[List[str], Dict[str, str]]:
        """Return variable names and label mapping for a study."""
        filters: Dict[str, Any] = {}
        if variable_whitelist is not None:
            filters["variableNames"] = variable_whitelist
        if form_whitelist is not None:
            filters["formIds"] = form_whitelist

        variables: List[VariableModel] = list(
            self.sdk.get_variables(
                study_key=study_key,
                **filters,
            )
        )
        if not variables:
            logger.warning(
                "No variables found for study '%s'. Returning empty DataFrame.",
                study_key,
            )
            return [], {}

        variable_keys = [v.variable_name for v in variables]
        label_map = {v.variable_name: v.label for v in variables}  # type: ignore
        return variable_keys, label_map  # type: ignore

    def _build_record_model(
        self, variable_keys: List[str], label_map: Dict[str, str]
    ) -> Type[BaseModel]:
        """Create a dynamic model for the record data payload."""
        fields: Dict[str, Tuple[Optional[Any], Any]] = {}
        for key in variable_keys:
            fields[key] = (
                Optional[Any],
                Field(None, alias=key, description=label_map.get(key, key)),
            )
        return create_model("RecordData", __base__=BaseModel, **fields)  # type: ignore

    def _fetch_records(
        self,
        study_key: str,
        visit_key: Optional[str] = None,
        extra_filters: Optional[Dict[str, Union[Any, Tuple[str, Any], List[Any]]]] = None,
    ) -> List[RecordModel]:
        """Fetch records for a study applying optional filters."""
        filters: Dict[str, Union[Any, Tuple[str, Any], List[Any]]] = (
            dict(extra_filters) if extra_filters else {}
        )
        if visit_key is not None:
            try:
                filters["visitId"] = int(visit_key)
            except ValueError:
                logger.warning(
                    "Invalid visit_key '%s'. Should be convertible to int. Fetching all records.",
                    visit_key,
                )
        try:
            return list(
                self.sdk.get_records(
                    study_key=study_key,
                    record_data_filter=None,
                    **filters,
                )
            )
        except Exception as exc:  # pragma: no cover - unexpected
            logger.error("Failed to fetch records for study '%s': %s", study_key, exc)
            return []

    def _iter_records(
        self,
        study_key: str,
        visit_key: Optional[str] = None,
        extra_filters: Optional[Dict[str, Union[Any, Tuple[str, Any], List[Any]]]] = None,
    ) -> Iterable[RecordModel]:
        """Implementation detail."""
        form_ids: set[Any] | None = None
        filters = dict(extra_filters) if extra_filters else {}
        if "formIds" in filters and isinstance(filters["formIds"], list):
            form_ids = set(filters["formIds"])
        elif "formId" in filters:
            form_ids = {filters["formId"]}

        loader = self._loader
        if loader is not None:
            sync_method = getattr(loader, "sync_records", None)
            iter_method = getattr(type(loader), "iter_cached_records", None)
            if callable(sync_method) and callable(iter_method):
                sync_method(study_key)
                return self._filter_records(
                    iter_method(loader, study_key, chunk_size=self._pipeline.chunk_size),
                    visit_key=visit_key,
                    form_ids=form_ids,
                )

        return self._fetch_records(
            study_key,
            visit_key,
            extra_filters=extra_filters,
        )

    def _filter_records(
        self,
        records: Iterable[RecordModel],
        *,
        visit_key: Optional[str],
        form_ids: set[Any] | None,
    ) -> Iterator[RecordModel]:
        """Implementation detail."""
        visit_id: int | None = None
        if visit_key is not None:
            try:
                visit_id = int(visit_key)
            except ValueError:
                logger.warning(
                    "Invalid visit_key '%s'. Should be convertible to int. Fetching all records.",
                    visit_key,
                )

        for record in records:
            if visit_id is not None and record.visit_id != visit_id:
                continue
            if form_ids is not None and record.form_id not in form_ids:
                continue
            yield record

    def _parse_record(
        self,
        rec: RecordModel,
        record_model: Type[BaseModel],
    ) -> Dict[str, Any]:
        """Perform  parse record operation."""
        meta = {
            "recordId": rec.record_id,
            "subjectKey": rec.subject_key,
            "visitId": rec.visit_id,
            "formId": rec.form_id,
            "recordStatus": rec.record_status,
            "dateCreated": (
                rec.date_created.isoformat()  # type: ignore[union-attr]
                if hasattr(rec.date_created, 'isoformat')
                else str(rec.date_created)
                if rec.date_created
                else None
            ),
        }
        data = rec.record_data if isinstance(rec.record_data, dict) else {}
        parsed = record_model(**data).model_dump(by_alias=False)
        return {**meta, **parsed}

    def _parse_records(
        self, records: Iterable[RecordModel], record_model: Type[BaseModel]
    ) -> Tuple[List[Dict[str, Any]], int]:
        """Parse raw records into row dictionaries and count failures."""
        rows: List[Dict[str, Any]] = []
        errors = 0
        for chunk_rows, chunk_errors in self._iter_parsed_rows(records, record_model):
            rows.extend(chunk_rows)
            errors += chunk_errors
        return rows, errors

    def _iter_parsed_rows(
        self,
        records: Iterable[RecordModel],
        record_model: Type[BaseModel],
    ) -> Iterator[Tuple[List[Dict[str, Any]], int]]:
        """Perform  iter parsed rows operation."""
        for chunk in iter_chunks(records, chunk_size=self._pipeline.chunk_size):
            rows: List[Dict[str, Any]] = []
            errors = 0
            for rec in chunk:
                try:
                    rows.append(self._parse_record(rec, record_model))
                except (ValidationError, TypeError) as exc:
                    errors += 1
                    logger.warning(
                        "Failed to parse record data for recordId %s: %s",
                        rec.record_id,
                        exc,
                    )
                except Exception as exc:  # pragma: no cover - unexpected
                    errors += 1
                    logger.error("Unexpected error processing recordId %s: %s", rec.record_id, exc)
            yield rows, errors

    def _build_dataframe(
        self,
        rows: List[Dict[str, Any]],
        variable_keys: List[str],
        label_map: Dict[str, str],
        use_labels: bool,
    ) -> pd.DataFrame:
        """Create the output DataFrame from parsed rows."""
        df = pd.DataFrame(rows)
        if df.empty:
            return df

        meta_cols = [
            "recordId",
            "subjectKey",
            "visitId",
            "formId",
            "recordStatus",
            "dateCreated",
        ]

        for key in variable_keys:
            if key not in df.columns:
                df[key] = pd.NA

        df = df[meta_cols + variable_keys]
        if use_labels:
            rename_map = {key: label_map.get(key, key) for key in variable_keys}
            df = df.rename(columns=rename_map)
        return df

    def iter_dataframes(
        self,
        study_key: str,
        visit_key: Optional[str] = None,
        use_labels_as_columns: bool = True,
        variable_whitelist: Optional[List[str]] = None,
        form_whitelist: Optional[List[int]] = None,
    ) -> Iterator[pd.DataFrame]:
        """Yield mapped record DataFrames in bounded chunks.

        Each yielded frame contains at most ``chunk_size`` mapped records from
        this mapper instance. Prefer this method over ``dataframe()`` when
        processing or exporting large studies so each chunk can be committed
        before the next batch is parsed.
        """
        if pd is None:
            raise ImportError(
                (
                    "pandas is required for RecordMapper.dataframe. Install "
                    "with 'pip install \"imednet[pandas]\"'."
                )
            )
        variable_keys, label_map = self._fetch_variable_metadata(
            study_key,
            variable_whitelist=variable_whitelist,
            form_whitelist=form_whitelist,
        )
        if not variable_keys:
            return

        record_model = self._build_record_model(variable_keys, label_map)
        extra_filters: Dict[str, Any] = {}
        if variable_whitelist is not None:
            extra_filters["variableNames"] = variable_whitelist
        if form_whitelist is not None:
            extra_filters["formIds"] = form_whitelist

        errors = 0
        yielded = False
        for rows, chunk_errors in self._iter_parsed_rows(
            self._iter_records(
                study_key,
                visit_key,
                extra_filters=extra_filters or None,
            ),
            record_model,
        ):
            errors += chunk_errors
            df = self._build_dataframe(rows, variable_keys, label_map, use_labels_as_columns)
            if df.empty:
                continue
            yielded = True
            yield df

        if errors:
            logger.warning("Encountered %s errors while parsing record data.", errors)
        if not yielded:
            logger.info(
                "No records processed successfully for study '%s' with the given filters.",
                study_key,
            )

    def build_hierarchy(
        self,
        study_key: str,
        visit_key: Optional[str] = None,
        use_labels_as_keys: bool = False,
        variable_whitelist: Optional[List[str]] = None,
        form_whitelist: Optional[List[int]] = None,
    ) -> List[Dict[str, Any]]:
        """Generate a nested JSON tree structure up to three levels deep.

        Outputs a Subject -> Visit -> Form tree of records. Maps variables
        using form-scoped models to prevent namespace collisions. Relational
        identifiers such as parent_record_id are populated dynamically based
        on hierarchy context.
        """
        from imednet_workflows.study_structure import get_study_structure

        study_struct = get_study_structure(self.sdk, study_key)

        # 1. Build form-scoped models
        form_models: Dict[int, Type[BaseModel]] = {}
        form_label_maps: Dict[int, Dict[str, str]] = {}

        for interval in study_struct.intervals:
            for form in interval.forms:
                if form_whitelist and form.form_id not in form_whitelist:
                    continue
                var_keys = [
                    v.variable_name
                    for v in form.variables
                    if not variable_whitelist or v.variable_name in variable_whitelist
                ]
                label_map = {v.variable_name: v.label for v in form.variables}  # type: ignore
                form_models[form.form_id] = self._build_record_model(var_keys, label_map)  # type: ignore
                form_label_maps[form.form_id] = label_map  # type: ignore

        extra_filters: Dict[str, Any] = {}
        if form_whitelist is not None:
            extra_filters["formIds"] = form_whitelist
        if variable_whitelist is not None:
            extra_filters["variableNames"] = variable_whitelist

        # 2. Fetch and iterate records
        records = self._iter_records(
            study_key,
            visit_key,
            extra_filters=extra_filters or None,
        )

        tree: Dict[str, Dict[str, Any]] = {}

        for rec in records:
            if rec.form_id not in form_models:
                continue

            model = form_models[rec.form_id]
            label_map = form_label_maps[rec.form_id]  # type: ignore

            try:
                parsed_data = self._parse_record(rec, model)
            except (ValidationError, TypeError) as exc:
                logger.warning(
                    "Failed to parse record data for recordId %s: %s",
                    rec.record_id,
                    exc,
                )
                continue
            except Exception as exc:  # pragma: no cover - unexpected
                logger.error("Unexpected error processing recordId %s: %s", rec.record_id, exc)
                continue

            if use_labels_as_keys:
                remapped: Dict[str, Any] = {}
                for k, v in parsed_data.items():
                    lbl = label_map.get(k)
                    remapped[lbl if lbl is not None else k] = v
                parsed_data = remapped

            # Automatically perform lookups for parent record identifiers using available metadata
            resolved_parent_id = getattr(rec, "parent_record_id", None)
            if not resolved_parent_id:
                resolved_parent_id = f"{rec.visit_id}_{rec.form_id}"

            if "parent_record_id" not in parsed_data or parsed_data.get("parent_record_id") is None:
                parsed_data["parent_record_id"] = resolved_parent_id
                # If we mapped to a label or alias, also try to set it there
                if use_labels_as_keys and "parentRecordId" in parsed_data:
                    parsed_data["parentRecordId"] = resolved_parent_id

            subj_key = rec.subject_key
            if subj_key not in tree:
                tree[subj_key] = {"subject_key": subj_key, "visits": {}}  # type: ignore

            subj_node = tree[subj_key]  # type: ignore

            visit_id = rec.visit_id
            if visit_id not in subj_node["visits"]:
                subj_node["visits"][visit_id] = {"visit_id": visit_id, "forms": {}}

            visit_node = subj_node["visits"][visit_id]

            form_id = rec.form_id
            if form_id not in visit_node["forms"]:
                visit_node["forms"][form_id] = {"form_id": form_id, "records": []}

            form_node = visit_node["forms"][form_id]
            form_node["records"].append(parsed_data)

        # 3. Convert dicts to lists
        result = []
        for subj_key, subj in tree.items():
            subj_visits = []
            for visit_id, visit in subj["visits"].items():
                visit_forms = []
                for form_id, form in visit["forms"].items():
                    visit_forms.append(form)
                visit["forms"] = visit_forms
                subj_visits.append(visit)
            subj["visits"] = subj_visits
            result.append(subj)

        return result

    def dataframe(
        self,
        study_key: str,
        visit_key: Optional[str] = None,
        use_labels_as_columns: bool = True,
        variable_whitelist: Optional[List[str]] = None,
        form_whitelist: Optional[List[int]] = None,
    ) -> pd.DataFrame:
        """Return a :class:`pandas.DataFrame` of records for a study.

        This method still materialises all yielded chunks into one DataFrame.
        For bounded-memory processing of large studies, prefer ``iter_dataframes()``.
        """
        if pd is None:
            raise ImportError(
                (
                    "pandas is required for RecordMapper.dataframe. Install "
                    "with 'pip install \"imednet[pandas]\"'."
                )
            )
        frames = list(
            self.iter_dataframes(
                study_key,
                visit_key=visit_key,
                use_labels_as_columns=use_labels_as_columns,
                variable_whitelist=variable_whitelist,
                form_whitelist=form_whitelist,
            )
        )
        if not frames:
            return pd.DataFrame()
        return pd.concat(frames, ignore_index=True)
