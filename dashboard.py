import streamlit as st
import pandas as pd
from pathlib import Path

# Page setup
st.set_page_config(
    page_title="Student College Allocation System",
    page_icon=":mortar_board:",
    layout="centered"
)

# Header
st.markdown("""
<div style="text-align: center; font-family: sans-serif;">
    <h1>🎓 Student College Allocation System</h1>
    <p>Enter your UniqueID below to check your college allocation.</p>
</div>
""", unsafe_allow_html=True)

# Load the assignment CSV
@st.cache_data
def load_data():
    path = Path("assignment_submission.csv")
    return pd.read_csv(path) if path.exists() else pd.DataFrame()
data = load_data()

# UniqueID input, styled
uid = st.text_input("🔑 Enter Your UniqueID:", key="uid_input", max_chars=10).strip()

if uid:
    with st.spinner("Searching..."):
        try:
            uid_num = int(uid)
            result = data[data["uniqueid"] == uid_num]
            if not result.empty:
                st.success("✅ Allocation Found!")
                st.markdown("#### Student Details")
                st.table(result[["uniqueid", "name", "gender", "caste", "rank"]])
                st.markdown("#### College Allotment")
                st.table(result[["collegeid", "institution", "prefnumber"]])
            else:
                st.error("No allocation found. Please check your UniqueID.")
        except ValueError:
            st.warning("Please enter a valid numeric UniqueID.")
else:
    st.info("Please enter your UniqueID to view the result.")

# Optional: sidebar for extra insights
with st.sidebar:
    st.header("Quick Stats")
    if not data.empty:
        st.metric("Total Students", len(data))
        st.metric(
            "Allocated Students",
            
            len(data[data["collegeid"].notna()])
        )
        st.metric(
            "Unallocated Students",
            len(data[data["collegeid"].isna()])
        )

