# iMednet Streamlit Dashboard Plugin

## Overview

`imednet-streamlit` provides interactive operational dashboards for iMednet EDC studies.

## Installation

### Prerequisites

- Python 3.10+
- Core SDK installed (`imednet`)
- Streamlit plugin installed (`imednet-streamlit`)

### Quick Start

```bash
pip install imednet-streamlit
imednet dashboard
imednet dashboard --port 9999
imednet dashboard --no-browser
```

## Authentication

Use the sidebar to connect:

1. Enter API Key (masked)
2. Enter Security Key (masked)
3. Enter Study Key
4. Click **Connect**

### Streamlit Secrets (shared deployments)

```toml
# .streamlit/secrets.toml (DO NOT COMMIT)
[imednet]
api_key = "your-api-key"
security_key = "your-security-key"
```

## Dashboard Pages

### Query Status Overview
- Open/closed query metrics
- Filters by status, annotation type, and date
- CSV/Excel export

### Subject Enrollment Overview
- Enrollment KPIs
- Trend and site-level summaries
- Download-ready table output

### Site Performance
- Site-level query rate KPIs
- Top-site chart truncation with `"Other"` bucket for large studies
- Query-rate highlighting in paginated tables

### Data Completeness
- Record status breakdown
- Subject × form completion heatmap
- Top incomplete forms with truncation defaults

## Configuration Reference

| Option | Description | Default |
|---|---|---|
| `--port` | Streamlit server port | `8501` |
| `--no-browser` | Disable automatic browser launch | `false` |
| Cache `ttl` | `@st.cache_data` TTL in seconds | `600` |

## Deployment

### Local
- Install plugin and run `imednet dashboard`.
- Provide credentials in the sidebar at runtime.

### Streamlit Community Cloud
- Add plugin dependencies to the deployed environment.
- Configure credentials with Streamlit secrets.

## Architecture Notes

Dashboard pages use SDK-only data access (`ImednetSDK`) and avoid direct HTTP clients. Heavy
tables render page slices (50/100/200 rows) and charts truncate long category lists to minimize
browser DOM load on very large studies.
