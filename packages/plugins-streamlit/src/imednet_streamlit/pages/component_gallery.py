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
    render_triage_drawer,
)
from imednet_workflows.triage_store import TriageStore

st.title("Component Gallery")
st.markdown(
    "Live preview gallery showcasing functional grids, charts, and drawers using mock datasets."
)

st.header("Charts")

# Mock data for charts
np.random.seed(42)
months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun"]
data = {
    "Month": months,
    "Enrollment": np.random.randint(10, 50, size=len(months)),
    "Dropout": np.random.randint(0, 10, size=len(months)),
    "Category": ["A", "B", "C", "A", "B", "C"],
}
df_charts = pd.DataFrame(data)

col1, col2 = st.columns(2)
with col1:
    st.subheader("Bar Chart")
    st.altair_chart(
        bar_chart(
            df_charts, x="Month", y="Enrollment", color="Category", title="Monthly Enrollment"
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
    pie_chart(df_charts, theta="Enrollment", color="Category", title="Enrollment by Category"),
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

st.dataframe(
    paginated_slice(
        df_grid, key="gallery_grid", default_page_size=10, page_size_options=(5, 10, 20, 50)
    ),
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
