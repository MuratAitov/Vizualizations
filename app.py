import streamlit as st

from hw2.showing_data import render_hw2
from hw3.hypercube import render_hw3

st.set_page_config(
    page_title="CPSC 481 Data Analysis and Communication",
    layout="wide",
)

st.markdown(
    """
    <style>
    .hw-card {
        border: 1px solid #d7d7d7;
        border-radius: 14px;
        padding: 16px 18px;
        background: linear-gradient(180deg, #ffffff 0%, #f6f7fb 100%);
        box-shadow: 0 6px 16px rgba(0, 0, 0, 0.06);
        min-height: 120px;
    }
    .hw-title {
        font-size: 18px;
        font-weight: 700;
        margin-bottom: 6px;
    }
    .hw-sub {
        font-size: 13px;
        color: #555555;
        margin: 0;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("CPSC 481 Data Analysis and Communication")
st.caption("Pick a homework window to open.")

if "selected_hw" not in st.session_state:
    st.session_state.selected_hw = "Showing Data"

st.markdown(
    """
    <div class="hw-card">
        <div class="hw-title">Showing Data</div>
        <p class="hw-sub">HW 2</p>
    </div>
    """,
    unsafe_allow_html=True,
)
if st.button("Open Showing Data", use_container_width=True):
    st.session_state.selected_hw = "Showing Data"

st.markdown(
    """
    <div class="hw-card">
        <div class="hw-title">Interactive Hypercube</div>
        <p class="hw-sub">HW 3</p>
    </div>
    """,
    unsafe_allow_html=True,
)
if st.button("Open Interactive Hypercube", use_container_width=True):
    st.session_state.selected_hw = "Interactive Hypercube"

st.divider()

selected_hw = st.session_state.selected_hw
if selected_hw == "Showing Data":
    render_hw2()
elif selected_hw == "Interactive Hypercube":
    render_hw3()
