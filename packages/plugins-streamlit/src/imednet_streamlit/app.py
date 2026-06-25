"""App module."""

from __future__ import annotations

import streamlit as st

from imednet_streamlit.auth import render_auth_sidebar

st.set_page_config(
    page_title="iMednet EDC Dashboard",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
)

# High contrast mode logic
if "high_contrast" not in st.session_state:
    st.session_state["high_contrast"] = (
        st.query_params.get("high_contrast", "false").lower() == "true"
    )


def toggle_high_contrast():
    """Handle the toggle high contrast process."""
    st.session_state["high_contrast"] = not st.session_state["high_contrast"]
    if st.session_state["high_contrast"]:
        st.query_params["high_contrast"] = "true"
    else:
        if "high_contrast" in st.query_params:
            del st.query_params["high_contrast"]


st.sidebar.toggle(
    "High Contrast Mode", value=st.session_state["high_contrast"], on_change=toggle_high_contrast
)

if st.session_state["high_contrast"]:
    st.markdown(
        """
        <style>
        /* High contrast mode CSS ensuring minimum contrast ratio 7:1 */
        html, body, [class*="st-"] {
            background-color: #000000 !important;
            color: #FFFFFF !important;
            border-color: #FFFFFF !important;
        }
        h1, h2, h3, h4, h5, h6, p, span, div {
            color: #FFFFFF !important;
        }
        button {
            background-color: #FFFFFF !important;
            color: #000000 !important;
            border: 2px solid #FFFFFF !important;
        }
        /* Ensure inputs and interactive elements are clearly visible */
        input, select, textarea {
            background-color: #000000 !important;
            color: #FFFFFF !important;
            border: 2px solid #FFFFFF !important;
        }
        /* Highly visible focus state for keyboard navigation */
        *:focus {
            outline: 3px solid #FFFF00 !important;
            outline-offset: 2px !important;
        }
        /* SVG charts */
        svg text {
            fill: #FFFFFF !important;
        }
        </style>
    """,
        unsafe_allow_html=True,
    )

import pandas as pd

original_altair_chart = st.altair_chart


def accessible_altair_chart(altair_chart, use_container_width=False, theme="streamlit", **kwargs):
    """Handle the accessible altair chart process."""
    title = getattr(altair_chart, "title", "Chart")
    if isinstance(title, dict) and "text" in title:
        title = title["text"]
    elif not isinstance(title, str):
        title = "Chart"

    df = getattr(altair_chart, "data", pd.DataFrame())

    if not hasattr(altair_chart, "description") or not getattr(altair_chart, "description", None):
        altair_chart = altair_chart.properties(description=f"Data visualization for {title}")

    original_altair_chart(
        altair_chart, use_container_width=use_container_width, theme=theme, **kwargs
    )

    if isinstance(df, pd.DataFrame) and not df.empty:
        with st.expander(f"Tabular Data View: {title}", expanded=False):
            st.dataframe(df, use_container_width=use_container_width)


from imednet.spi.utils import redact_sensitive_text

original_st_error = st.error
original_st_exception = st.exception
original_st_warning = st.warning
original_st_info = st.info


def _sanitize_body(body):
    """Handle the sanitize body process."""
    if isinstance(body, Exception):
        try:
            body_str = str(body)
        except Exception:
            body_str = "<unprintable exception>"
        redacted_msg = redact_sensitive_text(body_str)
        try:
            safe_ex = type(body)(redacted_msg)
            safe_ex.__traceback__ = body.__traceback__
            return safe_ex
        except Exception:
            safe_ex = Exception(f"{type(body).__name__}: {redacted_msg}")
            safe_ex.__traceback__ = body.__traceback__
            return safe_ex
    elif isinstance(body, str):
        return redact_sensitive_text(body)
    return body


def secure_st_error(body, *args, **kwargs):
    """Handle the secure st error process."""
    return original_st_error(_sanitize_body(body), *args, **kwargs)


def secure_st_exception(exception, *args, **kwargs):
    """Handle the secure st exception process."""
    return original_st_exception(_sanitize_body(exception), *args, **kwargs)


def secure_st_warning(body, *args, **kwargs):
    """Handle the secure st warning process."""
    return original_st_warning(_sanitize_body(body), *args, **kwargs)


def secure_st_info(body, *args, **kwargs):
    """Handle the secure st info process."""
    return original_st_info(_sanitize_body(body), *args, **kwargs)


st.error = secure_st_error
st.exception = secure_st_exception
st.warning = secure_st_warning
st.info = secure_st_info

st.altair_chart = accessible_altair_chart

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
publisher_wizard_page = st.Page("pages/publisher_wizard.py", title="Publisher Wizard", icon="🏛️")
data_lineage_page = st.Page("pages/data_lineage.py", title="Data Lineage", icon="🔭")
admin_page = st.Page("pages/admin.py", title="Enterprise Admin", icon="🏢")
conformance_portal = st.Page("pages/conformance.py", title="Accessibility Portal", icon="♿")

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
            publisher_wizard_page,
            data_lineage_page,
            admin_page,
            conformance_portal,
        ]
    )
else:
    nav = st.navigation([home_page, admin_page, conformance_portal])

nav.run()
