from __future__ import annotations

import streamlit as st

from imednet_streamlit.auth import render_auth_sidebar

st.set_page_config(
    page_title="iMednet EDC Dashboard",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
)

is_connected = render_auth_sidebar()

home_page = st.Page("pages/home.py", title="Home", icon="🏠", default=True)
queries_page = st.Page("pages/queries.py", title="Query Status", icon="🔍")
enrollment_page = st.Page("pages/enrollment.py", title="Subject Enrollment", icon="👥")
reporting_dashboard_page = st.Page(
    "pages/reporting_dashboard.py", title="Reporting Dashboard", icon="📊"
)
sites_page = st.Page("pages/sites.py", title="Site Performance", icon="🏥")
records_page = st.Page("pages/records.py", title="Data Completeness", icon="📋")
setup_wizard_page = st.Page("pages/setup_wizard.py", title="Setup Wizard", icon="🧭")
review_workbench_page = st.Page("pages/review_workbench.py", title="Review Workbench", icon="🧪")

if is_connected:
    nav = st.navigation(
        [
            home_page,
            queries_page,
            enrollment_page,
            reporting_dashboard_page,
            sites_page,
            records_page,
            setup_wizard_page,
            review_workbench_page,
        ]
    )
else:
    nav = st.navigation([home_page])

nav.run()
