import streamlit as st
import pandas as pd
from pathlib import Path

# -------------------------
# Page setup
# -------------------------
st.set_page_config(
    page_title="Student College Allocation System",
    page_icon="🎓",
    layout="wide"
)

# -------------------------
# Load the assignment CSV
# -------------------------
@st.cache_data
def load_data():
    path = Path("assignment_submission.csv")
    return pd.read_csv(path) if path.exists() else pd.DataFrame()

data = load_data()

# -------------------------
# Header
# -------------------------
st.markdown("""
<div style="text-align: center; font-family: sans-serif; padding: 10px;">
    <h1 style="color: #2E86C1;">🎓 Student College Allocation System</h1>
    <p style="font-size:18px;">Enter your <b>UniqueID</b> below to check your allocation details and explore overall admission insights.</p>
</div>
""", unsafe_allow_html=True)

# -------------------------
# UniqueID Search
# -------------------------
uid = st.text_input("🔑 Enter Your UniqueID:", key="uid_input", max_chars=10).strip()

if uid:
    with st.spinner("🔍 Searching records..."):
        try:
            uid_num = int(uid)
            result = data[data["uniqueid"] == uid_num]

            if not result.empty:
                student = result.iloc[0]

                # ✅ Success Message
                st.success(f"✅ Allocation found for **{student['name']}** (Rank {student['rank']})")

                col1, col2 = st.columns(2)

                # Student details
                with col1:
                    st.subheader("👤 Student Profile")
                    st.write(f"**UniqueID:** {student['uniqueid']}")
                    st.write(f"**Name:** {student['name']}")
                    st.write(f"**Gender:** {student['gender']}")
                    st.write(f"**Caste/Category:** {student['caste']}")
                    st.write(f"**Rank:** {student['rank']}")

                # College details
                with col2:
                    st.subheader("🏫 College Allotment")
                    if pd.notna(student['collegeid']):
                        st.write(f"**Institution:** {student['institution']}")
                        st.write(f"**College ID:** {student['collegeid']}")
                        st.write(f"**Preference Order Used:** {student['prefnumber']}")
                        # satisfaction check
                        if student['prefnumber'] == 1:
                            st.success("🎉 You got your **1st preference** college!")
                        else:
                            st.info(f"ℹ️ You were allotted your **{student['prefnumber']} preference**.")
                    else:
                        st.error("❌ No College Available for this student.")

            else:
                st.error("No allocation found. Please check your UniqueID.")

        except ValueError:
            st.warning("⚠️ Please enter a valid numeric UniqueID.")

else:
    st.info("ℹ️ Please enter your UniqueID to view your result.")

# -------------------------
# Sidebar: Overall Insights
# -------------------------
with st.sidebar:
    st.header("📊 Quick Stats")
    if not data.empty:
        total_students = len(data)
        allocated = len(data[data["collegeid"].notna()])
        unallocated = len(data[data["collegeid"].isna()])

        st.metric("👥 Total Students", total_students)
        st.metric("✅ Allocated Students", allocated)
        st.metric("❌ Unallocated Students", unallocated)

        st.divider()

        # Category-wise allocation
        st.subheader("🗂 Allocation by Category")
        cat_alloc = data.groupby("caste")["collegeid"].apply(lambda x: x.notna().sum())
        st.bar_chart(cat_alloc)

        # Top colleges filled
        st.subheader("🏫 Top 5 Colleges (by Allotments)")
        top_colleges = (
            data[data["collegeid"].notna()]
            .groupby("institution")["uniqueid"]
            .count()
            .sort_values(ascending=False)
            .head(5)
        )
        st.table(top_colleges)

# -------------------------
# Footer
# -------------------------
st.markdown("""
<hr>
<p style="text-align:center; font-size:14px; color:gray;">
Made by SPK with ❤️ using Streamlit 
</p>
""", unsafe_allow_html=True)
