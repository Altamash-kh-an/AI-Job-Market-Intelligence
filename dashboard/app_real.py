import streamlit as st
import requests
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()

API_URL = os.getenv("API_URL")

st.set_page_config(
    page_title="AI Job Market Intelligence Platform",
    layout="wide"
)

st.markdown("""
<style>

/* AI Heading */
.ai-title{
    font-size:32px;
    font-weight:700;
    color:#2E86DE;
    font-family:Arial,sans-serif;
    text-align:center;
    margin-bottom:20px;
}

/* AI Card */
.ai-box{
    background:#f8f9fa;
    padding:20px;
    border-radius:15px;
    border:1px solid #dcdcdc;
    box-shadow:0px 4px 10px rgba(0,0,0,0.08);
}

/* Input Label */
.ai-label{
    font-size:18px;
    font-weight:600;
    font-family:Verdana;
    color:#444;
}

</style>
""", unsafe_allow_html=True)

st.title("🚀 AI Job Market Intelligence Platform")
st.divider()

st.markdown(
    '<div class="ai-title">🤖 AI Job Market Assistant</div>',
    unsafe_allow_html=True
)


st.markdown(
    '<div class="ai-label">Ask anything about the job market</div>',
    unsafe_allow_html=True
)

question = st.text_input(
    "Ask AI",
    placeholder="Example: Highest paying job in Bangalore",
    label_visibility="collapsed"
)

if st.button("🚀 Ask AI", width="stretch"):

    if question.strip():

        with st.spinner("🤖 AI is analyzing..."):

            try:

                response = requests.post(
                    f"{API_URL}/ai/chat",
                    json={"question": question},
                    timeout=60
                )

                response.raise_for_status()

                result = response.json()

                if "answer" in result:
                    st.chat_message("assistant").write(result["answer"])

                elif "error" in result:
                    st.error(result["error"])

                else:
                    st.write(result)

            except Exception as e:
                st.error(f"Error : {e}")

    else:
        st.warning("Please enter a question.")

st.markdown("</div>", unsafe_allow_html=True)


@st.cache_data(ttl=300)
def load_jobs():

    response = requests.get(
        f"{API_URL}/jobs",
        timeout=60
    )

    response.raise_for_status()

    return pd.DataFrame(response.json())


df = load_jobs()

if df.empty:
    st.warning("No jobs found.")
    st.stop()

df.index = df.index + 1

# ---------------- Sidebar Filters ---------------- #

location = st.sidebar.selectbox(
    "Select Location",
    ["All"] + sorted(df["location"].dropna().unique())
)

if location != "All":
    df = df[df["location"] == location]

company = st.sidebar.selectbox(
    "Select Company",
    ["All"] + sorted(df["company_name"].dropna().unique())
)

if company != "All":
    df = df[df["company_name"] == company]

job_role = st.sidebar.selectbox(
    "Select Job Role",
    ["All"] + sorted(df["job_roles"].dropna().unique())
)

if job_role != "All":
    df = df[df["job_roles"] == job_role]

search = st.sidebar.text_input("Search Job Title")

if search:
    df = df[
        df["job_title"].str.contains(
            search,
            case=False,
            na=False
        )
    ]

st.sidebar.download_button(
    label="Download Filtered Data",
    data=df.to_csv(index=False).encode("utf-8"),
    file_name="filtered_jobs.csv",
    mime="text/csv",
    width="stretch"
)

# ---------------- Metrics ---------------- #

col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Jobs", len(df))
col2.metric("Total Companies", df["company_name"].nunique())
col3.metric("Total Locations", df["location"].nunique())
col4.metric(
    "Average Rating",
    round(df["rating"].fillna(0).mean(), 2)
)

st.divider()

st.subheader("PAN India Jobs Data")

st.dataframe(
    df,
    width="stretch",
    hide_index=True
)

st.divider()

# ---------------- Charts ---------------- #

col1, col2 = st.columns(2)

with col1:
    st.subheader("Top Job Roles")

    if not df.empty:
        st.bar_chart(df["job_roles"].value_counts())

with col2:
    st.subheader("Jobs by Location")

    if not df.empty:
        st.bar_chart(df["location"].value_counts())

st.divider()

col3, col4 = st.columns(2)

with col3:
    st.subheader("Top Companies")

    if not df.empty:
        st.bar_chart(
            df["company_name"]
            .value_counts()
            .head(10)
        )

with col4:
    st.subheader("Employment Status")

    if not df.empty:
        st.bar_chart(
            df["employment_status"]
            .value_counts()
        )

st.divider()

# ---------------- Footer ---------------- #

st.caption("© AI Job Market Intelligence Platform")