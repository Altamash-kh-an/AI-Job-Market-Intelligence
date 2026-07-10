import streamlit as st
import pandas as pd
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="AI Job Market Intelligence Platform", layout="wide")

st.title("🚀 AI Job Market Intelligence Platform")

conn = psycopg2.connect(
        host=os.getenv("DB_HOST"),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD")
    )

df = pd.read_sql("SELECT * FROM jobs", conn)
df.index = df.index + 1

location = st.sidebar.selectbox(
    "Select Location",
    ["All"] + list(df["location"].unique())
)

if location != "All":
    df = df[df["location"] == location]

    skill = st.sidebar.selectbox(
    "Select Skill",
    ["All"] + list(df["skill"].unique())
)
    
    if skill != "All":
     df = df[df["skill"] == skill]

    search = st.sidebar.text_input("Search Job Title")
    if search:
     df = df[df["job_title"].str.contains(search, case=False)]

    st.download_button(
    label="Download Filtered Data",
    data=df.to_csv(index=False),
    file_name="filtered_jobs.csv",
    mime="text/csv"
)

    

# Metrics
col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Jobs", len(df))
col2.metric("Total Locations", df["location"].nunique())
col3.metric("Total Skills", df["skill"].nunique())
col4.metric("Avg Experience", round(df["experience"].mean(), 1))


st.divider()

# Data Table
st.subheader("Jobs Data")
st.dataframe(df)

st.divider()

# Charts
col1, col2 = st.columns(2)

with col1:
    st.subheader("Top Skills")
    st.bar_chart(df["skill"].value_counts())

with col2:
    st.subheader("Jobs by Location")
    st.bar_chart(df["location"].value_counts())

conn.close()