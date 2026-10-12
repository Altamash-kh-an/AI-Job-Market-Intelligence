import pandas as pd
import streamlit as st

from api.database import get_connection

st.set_page_config(page_title="AI Job Market Intelligence Platform", layout="wide")

st.title("🚀 AI Job Market Intelligence Platform")

conn = get_connection()
try:
    df = pd.read_sql("SELECT * FROM pan_india_jobs", conn)
finally:
    conn.close()

location = st.sidebar.selectbox(
    "Select Location",
    ["All"] + sorted(df["location"].dropna().unique()),
)

if location != "All":
    df = df[df["location"] == location]

job_role = st.sidebar.selectbox(
    "Select Job Role",
    ["All"] + sorted(df["job_roles"].dropna().unique()),
)

if job_role != "All":
    df = df[df["job_roles"] == job_role]

search = st.sidebar.text_input("Search Job Title")
if search:
    df = df[df["job_title"].str.contains(search, case=False, na=False)]

st.download_button(
    label="Download Filtered Data",
    data=df.to_csv(index=False),
    file_name="filtered_jobs.csv",
    mime="text/csv",
)

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Jobs", len(df))
col2.metric("Total Locations", df["location"].nunique())
col3.metric("Total Job Roles", df["job_roles"].nunique())
col4.metric("Average Rating", round(df["rating"].dropna().mean(), 1))

st.divider()
st.subheader("Jobs Data")
st.dataframe(df)

st.divider()
col1, col2 = st.columns(2)

with col1:
    st.subheader("Top Job Roles")
    st.bar_chart(df["job_roles"].value_counts())

with col2:
    st.subheader("Jobs by Location")
    st.bar_chart(df["location"].value_counts())
