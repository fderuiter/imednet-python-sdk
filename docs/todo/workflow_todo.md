# Workflow Recipies

---

## 5.1 `record_mapper.py`

### Class & Signature

```python
class RecordMapper:
    def __init__(self,
                 variable_ep: VariableEndpoint,
                 record_ep: RecordEndpoint):
        self._vars = variable_ep
        self._recs = record_ep

    def dataframe(self,
                  study_key: str,
                  form_id: int,
                  visit_key: str | None = None) -> pandas.DataFrame:
        …
```

### Inputs

- **study_key**: iMednet study identifier.  
- **form_id**: numeric form identifier.  
- **visit_key** (optional): visit to scope to (e.g. “V1”).  

### Outputs

- A `pandas.DataFrame` where each row is one record instance, columns cover:
  - metadata (`subjectKey`, `visitKey`, `recordStatus`, `dateCreated`, …)
  - one column per variable on the form, filled from the record’s `recordData`.

### Build Steps

1. **Set context**  

   ```python
   self._vars._ctx.study_key = study_key
   self._recs._ctx.study_key = study_key
   ```

2. **Fetch Variables metadata**  

   ```python
   vars = self._vars.list(formId=form_id)
   ```

   citeturn1search4  
3. **Fetch Records**  

   ```python
   filters = {"formId": form_id}
   if visit_key: filters["visitKey"] = visit_key
   recs = self._recs.list(**filters)
   ```

   citeturn1search0  
4. **Assemble row dicts**  

   ```python
   rows = []
   for r in recs:
       row = {
         "subjectKey": r.subjectKey,
         "visitKey": r.visitKey,
         "recordStatus": r.recordStatus,
         "dateCreated": r.dateCreated,
         # then one entry per variable:
       }
       for v in vars:
           row[v.variableKey] = r.recordData.get(v.variableKey)
       rows.append(row)
   ```

5. **Return DataFrame**  

   ```python
   return pandas.DataFrame(rows)
   ```

---

## 5.2 `export_bundle.py`

### Function & Signature

```python
def export(study_key: str,
           out_dir: pathlib.Path,
           parquet: bool = False) -> pathlib.Path:
    …
```

### Inputs

- **study_key**: iMednet study identifier.  
- **out_dir**: path to write files.  
- **parquet**: when `True`, write `.parquet`, else `.csv`.

### Outputs

- The `Path` to `out_dir`, now containing one file per resource:  
  `studies.(csv|parquet)`, `variables…`, `records…`, `queries…`, `subjects…`, `visits…`, `sites…`, `codings…`, `recordRevisions…`.

### Build Steps

1. **Prepare directory**  

   ```python
   out_dir.mkdir(exist_ok=True)
   ```

2. **Loop through endpoints**  
   For each `(name, endpoint)` in  
   `{"studies": sdk.studies, "variables": sdk.variables, …}`:  

   ```python
   items = endpoint.list()       # e.g. StudyEndpoint.list() citeturn1search6
   df = pandas.DataFrame([i.__dict__ for i in items])
   path = out_dir / f"{name}.{ext}"
   if parquet:
       df.to_parquet(path)
   else:
       df.to_csv(path, index=False)
   ```

   - _Studies_ citeturn1search6  
   - _Variables_ citeturn1search4  
   - _Records_ citeturn1search0  
   - _Queries_ citeturn1search3  
   - _Subjects_ citeturn2search0  
   - _Visits_ citeturn1search7  
   - _Sites_ citeturn4view0  
   - _Codings_ (similar pattern)  
   - _Record Revisions_ (similar)  
3. **Return**  

   ```python
   return out_dir
   ```

---

## 5.3 `crf_progress.py`

### Function & Signature

```python
def progress(study_key: str) -> pandas.DataFrame:
    …
```

### Inputs

- **study_key**: iMednet study identifier.

### Outputs

- A DataFrame with one row per `formId` (and optionally `visitKey`), showing:
  - `total_subjects`
  - `completed_count`
  - `pct_complete`

### Build Steps

1. **Set context**  

   ```python
   subject_ep._ctx.study_key = study_key
   record_ep._ctx.study_key  = study_key
   ```

2. **Fetch Subjects**  

   ```python
   subs = subject_ep.list()
   total = len(subs)
   ```  

   citeturn2search0  
3. **Fetch Records**  

   ```python
   recs = record_ep.list()
   ```

   citeturn1search0  
4. **DataFrame & aggregation**  

   ```python
   df = pandas.DataFrame([r.__dict__ for r in recs])
   summary = (df
       .groupby("formId")
       .apply(lambda d: pd.Series({
         "total_subjects": total,
         "completed_count": d.query("recordStatus=='Record Complete'")["subjectKey"].nunique()
       }))
       .assign(pct_complete=lambda d: d.completed_count / d.total_subjects)
       .reset_index()
   )
   return summary
   ```

---

## 5.4 `query_log.py`

### Function & Signature

```python
def history(study_key: str,
            unresolved_only: bool = False) -> pandas.DataFrame:
    …
```

### Inputs

- **study_key**: iMednet study identifier.  
- **unresolved_only**: if `True`, only open queries.

### Outputs

- A DataFrame where each row is one comment on a query, with columns:
  `annotationId, subjectKey, variable, sequence, user, annotationStatus, comment, date`.

### Build Steps

1. **Set context**  

   ```python
   query_ep._ctx.study_key = study_key
   ```

2. **Build filter**  

   ```python
   params = {}
   if unresolved_only:
       params["state"] = "open"
   ```

   citeturn2search5  
3. **Fetch Queries**  

   ```python
   qs = query_ep.list(**params)
   ```  

   citeturn2search5  
4. **Flatten comments**  

   ```python
   rows = []
   for q in qs:
       for c in q.queryComments:
           rows.append({
             "annotationId":       q.annotationId,
             "subjectKey":         q.subjectKey,
             "variable":           q.variable,
             "sequence":           c.sequence,
             "user":               c.user,
             "annotationStatus":   c.annotationStatus,
             "comment":            c.comment,
             "date":               c.date
           })
   return pandas.DataFrame(rows)
   ```

---

## 5.5 `snapshot_diff.py`

### Function & Signature

```python
def diff(old_dir: pathlib.Path,
         new_dir: pathlib.Path) -> pandas.DataFrame:
    …
```

### Inputs

- **old_dir**, **new_dir**: two export‐bundle directories (each with matching files like `records.parquet`, `variables.csv`, etc.).

### Outputs

- A DataFrame listing all detected changes, with columns:
  `resource, key_field, field_name, old_value, new_value`.

### Build Steps

1. **Discover resources**  

   ```python
   files = {f.stem for f in old_dir.iterdir()}
   ```

2. **Loop & load**  

   ```python
   diffs = []
   for name in files:
       f1 = old_dir / f"{name}.parquet"
       f2 = new_dir / f"{name}.parquet"
       df_old = pandas.read_parquet(f1)
       df_new = pandas.read_parquet(f2)
       merged = df_old.merge(df_new,
                             on=key_cols(name),
                             how="outer",
                             suffixes=("_old","_new"),
                             indicator=True)
       # for each differing cell, append a diff row
       for col in df_old.columns:
           m = merged.query(f"{col}_old != {col}_new")
           for _,row in m.iterrows():
               diffs.append({
                   "resource":    name,
                   "key":         tuple(row[k] for k in key_cols(name)),
                   "field":       col,
                   "old_value":   row[f"{col}_old"],
                   "new_value":   row[f"{col}_new"],
               })
   return pandas.DataFrame(diffs)
   ```

   - `key_cols(name)` returns the primary key field(s) for that resource (e.g. `["recordId"]`, `["variableId"]`, …).
3. **Return** merged diffs.

---

With these detailed recipes—complete with inputs, outputs, method signatures, step-by-step logic, and exact API calls—you’ll have everything you need to implement each workflow module quickly and test it in isolation.
