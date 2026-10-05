import streamlit as st
import streamlit.components.v1 as components
import requests
import pandas as pd
import os
import time
from dotenv import load_dotenv

load_dotenv()

API_URL = os.getenv("API_URL")

st.set_page_config(
    page_title="AI Job Market Intelligence",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# CUSTOM UI / CSS
# ============================================================

st.markdown("""
<style>

/* ---------- GLOBAL ---------- */

.stApp {
    background:
        radial-gradient(circle at 15% 10%, rgba(37,99,235,0.15), transparent 28%),
        radial-gradient(circle at 85% 5%, rgba(124,58,237,0.13), transparent 25%),
        #080d18;
    color: #e5e7eb;
}

.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
    max-width: 1450px;
}

/* Hide Streamlit branding */
#MainMenu {
    visibility: hidden;
}

footer {
    visibility: hidden;
}

header {
    visibility: visible !important;
}


/* ---------- TOP HEADER ---------- */

.brand {
    text-align: center;
    padding: 10px 0 22px 0;
}

.brand-title {
    font-size: 34px;
    font-weight: 800;
    letter-spacing: -1px;
    color: #ffffff;
    margin-bottom: 5px;
}

.brand-title span {
    color: #60a5fa;
}

.brand-subtitle {
    color: #94a3b8;
    font-size: 15px;
}

.live-badge {
    display: inline-block;
    margin-top: 12px;
    padding: 5px 14px;
    border-radius: 20px;
    background: rgba(34,197,94,0.10);
    border: 1px solid rgba(34,197,94,0.35);
    color: #4ade80;
    font-size: 12px;
    font-weight: 700;
}


/* ---------- AI HERO ---------- */

.ai-container {
    background:
        linear-gradient(
            135deg,
            rgba(30,64,175,0.30),
            rgba(88,28,135,0.25)
        );
    border: 1px solid rgba(96,165,250,0.28);
    border-radius: 24px;
    padding: 30px;
    margin: 10px 0 30px 0;
    box-shadow:
        0 15px 45px rgba(0,0,0,0.35),
        inset 0 1px 0 rgba(255,255,255,0.04);
}

.ai-heading {
    text-align: center;
    font-size: 27px;
    font-weight: 800;
    color: #ffffff;
    margin-bottom: 5px;
}

.ai-description {
    text-align: center;
    color: #a5b4fc;
    font-size: 14px;
    margin-bottom: 20px;
}

.ai-icon {
    font-size: 36px;
    text-align: center;
    margin-bottom: 4px;
}


/* ---------- INPUT ---------- */

.stTextInput > div > div > input {
    background: #111827 !important;
    color: #ffffff !important;
    border: 1px solid #334155 !important;
    border-radius: 14px !important;
    padding: 14px 16px !important;
    font-size: 15px !important;
}

.stTextInput > div > div > input:focus {
    border: 1px solid #60a5fa !important;
    box-shadow: 0 0 0 2px rgba(96,165,250,0.12) !important;
}

.stTextInput > div > div > input::placeholder {
    color: #94a3b8 !important;
    opacity: 1 !important;
}

/* Search examples */
.search-examples {
    margin-top: -4px;
    margin-bottom: 12px;
    color: #94a3b8;
    font-size: 11px;
    line-height: 1.8;
}
.search-examples-title {
    color: #64748b;
    margin-bottom: 2px;
}
.search-example {
    color: #94a3b8;
}


/* ---------- BUTTON ---------- */

.stButton > button {
    background: linear-gradient(
        135deg,
        #2563eb,
        #7c3aed
    ) !important;

    color: white !important;
    border: none !important;
    border-radius: 13px !important;
    font-weight: 700 !important;
    min-height: 45px !important;

    box-shadow:
        0 8px 20px rgba(37,99,235,0.25);
}

.stButton > button:hover {
    transform: translateY(-1px);
    box-shadow:
        0 10px 25px rgba(124,58,237,0.35);
}


/* ---------- SUGGESTIONS ---------- */

.suggestion {
    text-align: center;
    color: #94a3b8;
    font-size: 12px;
    margin-top: 14px;
}


/* ---------- SECTION TITLES ---------- */

.section-title {
    color: #f8fafc;
    font-size: 21px;
    font-weight: 750;
    margin: 12px 0 18px 0;
}

.section-subtitle {
    color: #64748b;
    font-size: 12px;
}


/* ---------- METRIC CARDS ---------- */

.metric-card {
    background: rgba(15,23,42,0.78);
    border: 1px solid #1e293b;
    border-radius: 18px;
    padding: 20px;
    min-height: 105px;

    box-shadow:
        0 8px 25px rgba(0,0,0,0.20);
}

.metric-icon {
    font-size: 20px;
}

.metric-value {
    color: #ffffff;
    font-size: 26px;
    font-weight: 800;
    margin-top: 6px;
}

.metric-label {
    color: #94a3b8;
    font-size: 12px;
}


/* ---------- DATAFRAME ---------- */

[data-testid="stDataFrame"] {
    border: 1px solid #1e293b;
    border-radius: 14px;
    overflow: hidden;
}



/* ---------- SIDEBAR NAVIGATION BUTTONS ---------- */

[data-testid="stSidebar"] .stButton > button {
    width: 100%;
    min-height: 42px !important;
    font-size: 13px !important;
    padding: 8px 12px !important;
    white-space: nowrap !important;
    overflow: hidden !important;
}

/* ---------- SIDEBAR ---------- */

[data-testid="stSidebar"] {
    background:
        linear-gradient(
            180deg,
            #0b1220,
            #080d18
        );
    border-right: 1px solid #1e293b;
}

[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3,
[data-testid="stSidebar"] label {
    color: #e2e8f0 !important;
}


/* ---------- CHAT RESPONSE ---------- */

[data-testid="stChatMessage"] {
    background: rgba(15,23,42,0.85);
    border: 1px solid #334155;
    border-radius: 16px;
}


/* ---------- DIVIDER ---------- */

hr {
    border-color: #1e293b !important;
}


/* ---------- FOOTER ---------- */

.custom-footer {
    text-align: center;
    color: #64748b;
    font-size: 12px;
    padding: 25px 0 5px 0;
}

/* ---------- RESPONSIVE MOBILE LAYOUT ---------- */

@media (max-width: 768px) {

    .block-container {
        padding-top: 1rem !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
    }

    .brand-title {
        font-size: 25px !important;
    }

    .brand-subtitle {
        font-size: 12px !important;
    }

    .ai-container {
        padding: 22px 15px !important;
        border-radius: 18px !important;
        margin-top: 6px !important;
    }

    .ai-heading {
        font-size: 21px !important;
    }

    .ai-description {
        font-size: 12px !important;
    }

    .stTextInput > div > div > input {
        font-size: 14px !important;
    }

    .metric-card {
        padding: 13px !important;
        min-height: 85px !important;
    }

    .metric-value {
        font-size: 20px !important;
    }

    .metric-label {
        font-size: 10px !important;
    }

    .section-title {
        font-size: 18px !important;
    }

    [data-testid="stDataFrame"] {
        font-size: 11px !important;
    }

    /* Keep the sidebar usable when opened on a phone. */
    [data-testid="stSidebar"] {
        min-width: 280px !important;
        max-width: 85vw !important;
    }

    [data-testid="stSidebar"] .stButton > button {
        min-height: 44px !important;
        font-size: 13px !important;
    }
}

</style>
""", unsafe_allow_html=True)


# ============================================================
# HEADER
# ============================================================

st.html("""
<div id="ai-top" class="brand">
    <div class="brand-title">🤖 AI <span>Job Market</span> Intelligence</div>
    <div class="brand-subtitle">Intelligent insights from India's job market</div>
    <div class="live-badge">● LIVE MARKET DATA</div>
</div>
""")


# ============================================================
# AI ASSISTANT - TOP
# ============================================================
st.html("""
<div class="ai-container">
    <div class="ai-icon">🔮</div>
    <div class="ai-heading">AI Job Market Assistant</div>
    <div class="ai-description">
        Ask anything about jobs, salaries, companies and locations
    </div>
</div>
""")


st.html('<div id="ai-input-target"></div>')

question = st.text_input(
    "Ask AI",
    placeholder="Example: Highest paying job in Bangalore",
    label_visibility="collapsed"
)

ask_col1, ask_col2, ask_col3 = st.columns([1, 2, 1])

with ask_col2:

    if st.button(
        "🚀  Ask AI",
        width="stretch"
    ):

        if question.strip():

            with st.spinner("🤖 AI is analyzing the job market..."):

                try:

                    response = requests.post(
                        f"{API_URL}/ai/chat",
                        json={"question": question},
                        timeout=60
                    )

                    response.raise_for_status()

                    result = response.json()

                    if "answer" in result:

                        st.chat_message(
                            "assistant",
                            avatar="🤖"
                        ).write(result["answer"])

                    elif "error" in result:

                        st.error(result["error"])

                    else:

                        st.write(result)

                except Exception as e:

                    st.error(f"Error : {e}")

        else:

            st.warning("Please enter a question.")


st.markdown("""
<div class="suggestion">
💡 Try: Highest paying job in Bangalore
&nbsp;&nbsp; • &nbsp;&nbsp;
Python jobs in Delhi
&nbsp;&nbsp; • &nbsp;&nbsp;
Top companies in Mumbai
</div>
""", unsafe_allow_html=True)


# ============================================================
# LOAD JOBS
# ============================================================

@st.cache_data(ttl=300)
def load_jobs():

    for attempt in range(3):

        try:

            response = requests.get(
                f"{API_URL}/jobs",
                timeout=60
            )

            if response.status_code == 200:

                return pd.DataFrame(
                    response.json()
                )

            if response.status_code == 429:

                if attempt < 2:

                    time.sleep(5)
                    continue

                st.error(
                    "Jobs API is temporarily busy. Please refresh the page."
                )

                return pd.DataFrame()

            response.raise_for_status()

        except Exception as e:

            if attempt == 2:

                st.error(f"Jobs API Error: {e}")

                return pd.DataFrame()

            time.sleep(3)

    return pd.DataFrame()


df = load_jobs()


if df.empty:

    st.warning("No jobs found.")
    st.stop()


df.index = df.index + 1


# ============================================================
# SIDEBAR FILTERS / NAVIGATION
# ============================================================

if "dashboard_view" not in st.session_state:
    st.session_state["dashboard_view"] = "table"

if "scroll_target" not in st.session_state:
    st.session_state["scroll_target"] = None

if "nav_counter" not in st.session_state:
    st.session_state["nav_counter"] = 0

if "focus_ai_input" not in st.session_state:
    st.session_state["focus_ai_input"] = False

st.sidebar.markdown("## 🔎 Job Explorer")
st.sidebar.caption("Filter the Indian job market")

# Always visible: jump to the AI question box.
if st.sidebar.button(
    "🤖 ASK AI",
    width="stretch",
    key="ask_ai_nav"
):
    st.session_state["scroll_target"] = "ai-input-target"
    st.session_state["focus_ai_input"] = True
    st.session_state["nav_counter"] += 1

location = st.sidebar.selectbox(
    "📍 Location",
    ["All"] + sorted(
        df["location"].dropna().unique()
    ),
    key="location_filter"
)

if location != "All":
    df = df[df["location"] == location]

company = st.sidebar.selectbox(
    "🏢 Company",
    ["All"] + sorted(
        df["company_name"].dropna().unique()
    ),
    key="company_filter"
)

if company != "All":
    df = df[df["company_name"] == company]

job_role = st.sidebar.selectbox(
    "💼 Job Role",
    ["All"] + sorted(
        df["job_roles"].dropna().unique()
    ),
    key="job_role_filter"
)

if job_role != "All":
    df = df[df["job_roles"] == job_role]

search = st.sidebar.text_input(
    "🔍 Search Job Title",
    placeholder="Type a job title...",
    key="job_search"
)

st.sidebar.markdown(
    """
    <div class="search-examples">
        <div class="search-examples-title">Examples:</div>
        <div class="search-example">💻 Java Developer</div>
        <div class="search-example">🐍 Python Developer</div>
    </div>
    """,
    unsafe_allow_html=True
)

if search:
    df = df[
        df["job_title"].str.contains(
            search,
            case=False,
            na=False
        )
    ]

# Detect every filter change.
current_filters = (location, company, job_role, search)
previous_filters = st.session_state.get("_previous_filters")

filters_changed = (
    previous_filters is not None
    and previous_filters != current_filters
)

st.session_state["_previous_filters"] = current_filters

# Any filter change always returns to the table.
if filters_changed:
    st.session_state["dashboard_view"] = "table"
    st.session_state["scroll_target"] = "jobs-table"
    st.session_state["nav_counter"] += 1

# Independent navigation buttons.
# Both are always visible and each only performs its own action.
if st.sidebar.button(
    "📋 VIEW TABLE",
    width="stretch",
    key="view_table_nav"
):
    st.session_state["scroll_target"] = "jobs-table"
    st.session_state["nav_counter"] += 1

if st.sidebar.button(
    "📊 VIEW CHART",
    width="stretch",
    key="view_chart_nav"
):
    st.session_state["scroll_target"] = "charts-section"
    st.session_state["nav_counter"] += 1

st.sidebar.divider()

st.sidebar.download_button(
    label="⬇️ Download Filtered Data",
    data=df.to_csv(index=False).encode("utf-8"),
    file_name="filtered_jobs.csv",
    mime="text/csv",
    width="stretch"
)


# ============================================================
# MARKET OVERVIEW
# ============================================================

st.markdown(
    '<div class="section-title">📊 Market Overview</div>',
    unsafe_allow_html=True
)


col1, col2, col3, col4 = st.columns(4)


with col1:

    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-icon">💼</div>
            <div class="metric-value">{len(df):,}</div>
            <div class="metric-label">Total Jobs</div>
        </div>
        """,
        unsafe_allow_html=True
    )


with col2:

    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-icon">🏢</div>
            <div class="metric-value">
                {df["company_name"].nunique():,}
            </div>
            <div class="metric-label">Companies</div>
        </div>
        """,
        unsafe_allow_html=True
    )


with col3:

    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-icon">📍</div>
            <div class="metric-value">
                {df["location"].nunique():,}
            </div>
            <div class="metric-label">Locations</div>
        </div>
        """,
        unsafe_allow_html=True
    )


with col4:

    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-icon">⭐</div>
            <div class="metric-value">
                {round(df["rating"].fillna(0).mean(), 2)}
            </div>
            <div class="metric-label">Average Rating</div>
        </div>
        """,
        unsafe_allow_html=True
    )


st.divider()


# ============================================================
# JOB DATA / MARKET CHARTS
# ============================================================

# -------------------- JOB TABLE --------------------

st.markdown(
    '<div id="jobs-table" class="section-title">📋 PAN India Jobs</div>',
    unsafe_allow_html=True
)

st.caption("Explore available job opportunities")

st.dataframe(
    df,
    width="stretch",
    hide_index=True
)

st.divider()

# -------------------- MARKET CHARTS --------------------

st.markdown(
    '<div id="charts-section" class="section-title">📈 Market Insights</div>',
    unsafe_allow_html=True
)

st.caption("Explore job market trends for the selected filters")

col1, col2 = st.columns(2)

with col1:
    st.markdown("### 💼 Top Job Roles")
    if not df.empty:
        st.bar_chart(
            df["job_roles"].value_counts()
        )

with col2:
    st.markdown("### 📍 Jobs by Location")
    if not df.empty:
        st.bar_chart(
            df["location"].value_counts()
        )

st.divider()

col3, col4 = st.columns(2)

with col3:
    st.markdown("### 🏢 Top Companies")
    if not df.empty:
        st.bar_chart(
            df["company_name"].value_counts().head(10)
        )

with col4:
    st.markdown("### 👔 Employment Status")
    if not df.empty:
        st.bar_chart(
            df["employment_status"].value_counts()
        )

# AUTO NAVIGATION
# ============================================================

scroll_target = st.session_state.get("scroll_target")
focus_ai_input = st.session_state.get("focus_ai_input", False)

if scroll_target or focus_ai_input:
    nav_id = st.session_state.get("nav_counter", 0)

    components.html(
        f"""
        <script>
        (function () {{
            const targetId = {scroll_target!r};
            const shouldFocusAI = {str(focus_ai_input).lower()};
            const navId = {nav_id};
            let attempts = 0;
            const maxAttempts = 30;

            function getAIInput(doc) {{
                const inputs = Array.from(doc.querySelectorAll("input"));
                return inputs.find(function (input) {{
                    return input.placeholder ===
                        "Example: Highest paying job in Bangalore";
                }});
            }}

            function navigate() {{
                try {{
                    const doc = window.parent.document;

                    if (targetId) {{
                        const target = doc.getElementById(targetId);

                        if (target) {{
                            target.scrollIntoView({{
                                behavior: "smooth",
                                block: "start"
                            }});
                        }}
                    }}

                    if (shouldFocusAI) {{
                        const input = getAIInput(doc);

                        if (input) {{
                            input.focus();
                            return true;
                        }}
                    }} else if (targetId) {{
                        return true;
                    }}
                }} catch (error) {{
                    console.log("Auto navigation error:", error);
                }}

                return false;
            }}

            function retry() {{
                if (navigate()) {{
                    return;
                }}

                attempts += 1;

                if (attempts < maxAttempts) {{
                    setTimeout(retry, 120);
                }}
            }}

            // navId makes every click/filter event a fresh navigation request.
            setTimeout(retry, 200);
        }})();
        </script>
        """,
        height=0
    )

    st.session_state["scroll_target"] = None
    st.session_state["focus_ai_input"] = False


# Disable browser autocomplete/history dropdown on the job-title search.
# This prevents the browser's saved suggestions from covering our own examples.
components.html(
    """
    <script>
    (function () {
        let attempts = 0;
        const maxAttempts = 20;

        function disableSearchAutocomplete() {
            try {
                const doc = window.parent.document;
                const inputs = Array.from(doc.querySelectorAll("input"));

                const searchInput = inputs.find(function (input) {
                    return input.placeholder === "Type a job title...";
                });

                if (searchInput) {
                    searchInput.setAttribute("autocomplete", "off");
                    searchInput.setAttribute("autocorrect", "off");
                    searchInput.setAttribute("autocapitalize", "off");
                    searchInput.setAttribute("spellcheck", "false");
                    return true;
                }
            } catch (error) {
                console.log("Search autocomplete setup unavailable", error);
            }

            attempts += 1;
            if (attempts < maxAttempts) {
                setTimeout(disableSearchAutocomplete, 100);
            }
            return false;
        }

        setTimeout(disableSearchAutocomplete, 100);
    })();
    </script>
    """,
    height=0
)

# ============================================================
# FOOTER
# ============================================================

st.markdown("""
<div class="custom-footer">
    🤖 AI Job Market Intelligence Platform
    &nbsp; • &nbsp;
    Built with Python, FastAPI, Streamlit & PostgreSQL
</div>
""", unsafe_allow_html=True)