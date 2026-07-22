"""Live preview gallery showcasing interactive UI components."""

import uuid

import numpy as np
import pandas as pd
import streamlit as st

from imednet.spi.models import TriageItem, TriageStatus
from imednet_streamlit.components import (
    bar_chart,
    line_chart,
    paginated_slice,
    pie_chart,
)
from imednet_streamlit.components.triage_drawer import render_triage_drawer
from imednet_streamlit.utils.triage_store import TriageStore

st.set_page_config(page_title="Component Gallery", layout="wide")
st.title("Component Gallery")

st.markdown(
    "A showcase of the reusable UI components provided by the Streamlit plugin. "
    "Use this gallery to preview styles and interactions before integrating them into workflows."
)

st.header("Charts")

# Mock data for charts
df_charts = pd.DataFrame(
    {
        "Month": ["Jan", "Feb", "Mar", "Apr"] * 2,
        "Category": ["A", "A", "A", "A", "B", "B", "B", "B"],
        "Enrollment": [10, 25, 45, 60, 5, 15, 30, 40],
    }
)

col1, col2 = st.columns(2)
with col1:
    st.subheader("Bar Chart")
    st.altair_chart(
        bar_chart(
            df_charts, x="Month", y="Enrollment", color="Category", title="Enrollment by Month"
        ),
        use_container_width=True,
    )

with col2:
    st.subheader("Line Chart")
    st.altair_chart(
        line_chart(
            df_charts, x="Month", y="Enrollment", color="Category", title="Enrollment Trend"
        ),
        use_container_width=True,
    )

st.subheader("Pie Chart")
st.altair_chart(
    pie_chart(df_charts, color="Category", theta="Enrollment", title="Enrollment by Category"),
    use_container_width=True,
)


st.header("Paginated Grid")
# Mock data for paginated grid
df_grid = pd.DataFrame(
    {
        "ID": range(1, 101),
        "Name": [f"Subject {i}" for i in range(1, 101)],
        "Score": np.random.uniform(50.0, 100.0, 100).round(2),
        "Active": np.random.choice([True, False], 100),
    }
)

page_size = st.slider("Grid Page Size", min_value=5, max_value=50, value=10, step=5)
st.dataframe(
    paginated_slice(df_grid, key="gallery_grid", default_page_size=page_size),
    use_container_width=True,
)


st.header("Triage Drawer")
# Initialize a mock in-memory triage store and item
mock_db_path = f"file:mock_triage_{uuid.uuid4().hex}?mode=memory&cache=shared"
store = TriageStore(db_path=mock_db_path)
item = TriageItem(
    item_id=str(uuid.uuid4()),
    study_key="MOCK_STUDY",
    status=TriageStatus.NEW,
    severity="high",
)
store.upsert_item(item)

# Render the drawer component interactively
st.markdown("Interact with the drawer below to see state changes:")
render_triage_drawer(
    store=store, item=item, assignee_options=["Alice", "Bob"], current_user="Alice"
)
