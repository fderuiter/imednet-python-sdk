=============================
Streamlit Dashboard Reference
=============================

Dashboard Pages
---------------

Query Status Overview
^^^^^^^^^^^^^^^^^^^^^
- Open/closed query metrics
- Filters by status, annotation type, and date
- CSV/Excel export

Subject Enrollment Overview
^^^^^^^^^^^^^^^^^^^^^^^^^^^
- Enrollment KPIs
- Trend and site-level summaries
- Download-ready table output

Site Performance
^^^^^^^^^^^^^^^^
- Site-level query rate KPIs
- Query rate = total open queries / active subjects for the selected time window
- Conditional formatting thresholds: green (< 0.5), amber (0.5–1.0), red (> 1.0)
- Top-site chart truncation with ``"Other"`` bucket for large studies
- Query-rate highlighting in paginated tables

Data Completeness
^^^^^^^^^^^^^^^^^
- Record status breakdown
- Subject × form completion heatmap
- Top incomplete forms with truncation defaults
- Large studies may load slower; narrow filters before exporting very large tables

Review Workbench
^^^^^^^^^^^^^^^^
- KPI cards showing open queue count, items with SLA aging > 72 hours, and resolved count
- Color-coded severity pills (red for Critical/Severe, amber for Warning, blue for Info)
- Filterable queue grid by severity, category (Adverse Event, Deviation, Deficiency), and assignee
- Subject key search across all queue items
- Triage drawer for item assignment, annotation, and status transition
- Backed by the local ``TriageStore`` SQLite database (default: ``~/.imednet/triage.sqlite3``)

Configuration Reference
-----------------------

.. list-table::
   :header-rows: 1

   * - Option
     - Description
     - Default
   * - ``--port``
     - Streamlit server port
     - ``8501``
   * - ``--no-browser``
     - Disable automatic browser launch
     - ``false``
   * - Cache ``ttl``
     - ``@st.cache_data`` TTL in seconds
     - ``600``


Architecture Notes
------------------

Dashboard pages use SDK-only data access (``ImednetSDK``) and avoid direct HTTP clients. Heavy
tables render page slices (50/100/200 rows) and charts truncate long category lists to minimize
browser DOM load on very large studies.
