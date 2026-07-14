import streamlit as st
import requests
import pandas as pd
import logging
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
    font-family:Arial, sans-serif;
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
st.markdown('<div class="ai-box">', unsafe_allow_html=True)

st.markdown(
    '<div class="ai-label">Ask anything about the job market</div>',
    unsafe_allow_html=True
)

question = st.text_input(
    "",
    placeholder="Example: Highest paying job in Bangalore"
)

if st.button("🚀 Ask AI", use_container_width=True):

    with st.spinner("🤖 AI is analyzing..."):

       response = requests.post(
    f"{API_URL}/ai/chat",
    json={"question": question}
    )

    answer = response.json()

    if "answer" in answer:
        st.chat_message("assistant").write(answer["answer"])

    elif "error" in answer:
        st.error(answer["error"])

    else:
        st.write(answer)
    st.markdown("</div>", unsafe_allow_html=True)




logger = logging.getLogger(__name__)

# @st.cache_data(ttl=300)

def load_jobs():

    response = requests.get(f"{API_URL}/jobs", timeout=60)

    logger.warning(f"Status = {response.status_code}")

    logger.warning(response.text[:500])   # sirf first 500 characters

    response.raise_for_status()

    data = response.json()

    return pd.DataFrame(data)

   
df = load_jobs()

logger.warning("A")

df.index = df.index + 1

logger.warning("B")

location = st.sidebar.selectbox(
    "Select Location",
    ["All"] + sorted(df["location"].unique())
)

logger.warning("C")

if location != "All":
    df = df[df["location"] == location]

logger.warning("D")

company = st.sidebar.selectbox(
    "Select Company",
    ["All"] + sorted(df["company_name"].dropna().unique())
)

logger.warning("E")

if company != "All":
    df = df[df["company_name"] == company]

logger.warning("F")

job_role = st.sidebar.selectbox(
    "Select Job Role",
    ["All"] + sorted(df["job_roles"].unique())
)

logger.warning("G")

if job_role != "All":
    df = df[df["job_roles"] == job_role]

logger.warning("H")


search = st.sidebar.text_input("Search Job Title")

if search:
    df = df[df["job_title"].str.contains(search, case=False)]


st.sidebar.download_button(
    label="Download Filtered Data",
    data=df.to_csv(index=False),
    file_name="filtered_jobs.csv",
    mime="text/csv"
)

col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Jobs", len(df))
col2.metric("Total Companies", df["company_name"].nunique())
col3.metric("Total Locations", df["location"].nunique())
col4.metric("Average Rating", round(df["rating"].mean(), 2))
st.divider()



st.subheader("PAN India Jobs Data")
#st.dataframe(df)



st.divider()

col1, col2 = st.columns(2)

with col1:
    st.subheader("Top Job Roles")
    st.bar_chart(df["job_roles"].value_counts())

with col2:
    st.subheader("Jobs by Location")
    st.bar_chart(df["location"].value_counts())

st.divider()

col3, col4 = st.columns(2)

with col3:
    st.subheader("Top Companies")
    st.bar_chart(df["company_name"].value_counts().head(10))

with col4:
    st.subheader("Employment Status")
    st.bar_chart(df["employment_status"].value_counts())
    

