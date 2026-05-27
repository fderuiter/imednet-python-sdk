# imednet-streamlit

Interactive Streamlit reporting dashboards for iMednet EDC.

## Install

```bash
pip install imednet-streamlit
```

Or from the workspace source:

```bash
pip install ./packages/plugins-streamlit
```

## Launch via CLI

Once installed alongside the core SDK, launch the dashboard directly:

```bash
imednet dashboard
```

Use `--port` to override the default port (8501) and `--no-browser` to suppress
automatic browser launch:

```bash
imednet dashboard --port 8080 --no-browser
```

## Launch directly with Streamlit

```bash
streamlit run "$(python -c 'import imednet_streamlit.app as app; print(app.__file__)')"
```

## Features

- **Multi-page navigation** — Home, Query Status, Subject Enrollment, Site Performance,
  Data Completeness, and Data Lineage views.
- **Secure credential management** — API key and security key are masked inputs stored
  in `st.session_state`; never logged or persisted.
- **Caching** — All heavy API calls are decorated with `@st.cache_data(ttl=600)` to
  prevent rate-limiting on re-renders.
- **SDK-only data access** — All network calls go through `ImednetSDK`, inheriting
  the built-in retry policies and error handling.
- **Altair charts** — Bar, line, and pie charts using the iMednet brand palette.
- **CSV / Excel exports** — One-click download buttons on every data table.

## Pages

| Page | Description |
|------|-------------|
| Home | Connection status and navigation guide |
| Query Status | Open/closed query breakdown with trend charts |
| Subject Enrollment | Enrollment funnel and site-level summaries |
| Site Performance | Per-site query rate metrics and rankings |
| Data Completeness | Record status heatmap and form-level summaries |
| Data Lineage | Drill-down from metrics to raw records, mapping rules, and canonical models |
