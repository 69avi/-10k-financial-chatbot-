"""
app.py  —  AI Financial Analysis Chatbot
Run with: streamlit run app.py
"""

import streamlit as st
import pandas as pd
from engine import answer_query, get_sample_questions

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="10-K Financial Chatbot",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=IBM+Plex+Sans:wght@300;400;600&display=swap');

    html, body, [class*="css"] {
        font-family: 'IBM Plex Sans', sans-serif;
    }
    .stApp { background-color: #0d1117; }

    .chat-bubble-user {
        background: #1c2a3a;
        border-left: 3px solid #58a6ff;
        padding: 12px 16px;
        border-radius: 0 8px 8px 0;
        margin: 8px 0;
        color: #e6edf3;
        font-size: 0.95rem;
    }
    .chat-bubble-bot {
        background: #161b22;
        border-left: 3px solid #3fb950;
        padding: 12px 16px;
        border-radius: 0 8px 8px 0;
        margin: 8px 0;
        color: #e6edf3;
        font-size: 0.95rem;
        white-space: pre-wrap;
    }
    .metric-card {
        background: #161b22;
        border: 1px solid #30363d;
        border-radius: 8px;
        padding: 16px;
        text-align: center;
    }
    .metric-card .value {
        font-family: 'IBM Plex Mono', monospace;
        font-size: 1.4rem;
        font-weight: 600;
        color: #58a6ff;
    }
    .metric-card .label {
        font-size: 0.75rem;
        color: #8b949e;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-top: 4px;
    }
    .pill {
        display: inline-block;
        background: #1c2a3a;
        border: 1px solid #58a6ff44;
        color: #58a6ff;
        border-radius: 20px;
        padding: 4px 12px;
        font-size: 0.78rem;
        margin: 3px;
        cursor: pointer;
    }
    h1 { color: #e6edf3 !important; font-weight: 600 !important; }
    h2, h3 { color: #c9d1d9 !important; }
    .stTextInput input {
        background: #161b22 !important;
        border: 1px solid #30363d !important;
        color: #e6edf3 !important;
        border-radius: 8px !important;
        font-family: 'IBM Plex Sans', sans-serif !important;
    }
    .stTextInput input:focus {
        border-color: #58a6ff !important;
        box-shadow: 0 0 0 2px #58a6ff22 !important;
    }
    .stButton button {
        background: #21262d !important;
        color: #c9d1d9 !important;
        border: 1px solid #30363d !important;
        border-radius: 6px !important;
    }
    .stButton button:hover {
        background: #30363d !important;
        border-color: #58a6ff !important;
        color: #58a6ff !important;
    }
    .sidebar .sidebar-content { background: #161b22; }
    div[data-testid="stSidebarContent"] { background: #161b22; }
    .stFileUploader { border: 1px dashed #30363d !important; border-radius: 8px; }
</style>
""", unsafe_allow_html=True)


# ── Session state ─────────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []
if "df" not in st.session_state:
    st.session_state.df = None
if "pending_query" not in st.session_state:
    st.session_state.pending_query = ""


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 📂 Data Source")
    uploaded = st.file_uploader(
        "Upload financial CSV", type=["csv"],
        help="Columns: Company, Year, Revenue, Net_Income, EPS, etc."
    )

    if uploaded:
        df = pd.read_csv(uploaded)
        st.session_state.df = df
        st.success(f"✅ Loaded {len(df)} rows")
    else:
        if st.button("▶ Use Sample Data (FAANG)"):
            st.session_state.df = pd.read_csv("data/sample_financials.csv")
            st.success("✅ Sample data loaded!")

    if st.session_state.df is not None:
        df = st.session_state.df
        st.markdown("---")
        st.markdown("**Companies detected:**")
        for co in df["Company"].unique():
            st.markdown(f"• {co}")

        st.markdown("**Years:**")
        years = sorted(df["Year"].unique())
        st.markdown(f"`{min(years)}` → `{max(years)}`")

        st.markdown("---")
        st.markdown("**Available metrics:**")
        numeric_cols = df.select_dtypes("number").columns.drop("Year", errors="ignore")
        for col in numeric_cols:
            st.markdown(f"  `{col}`")

    st.markdown("---")
    st.markdown("**📌 Project by Priyanshu Sajwan**")
    st.markdown("[GitHub](https://github.com) · [LinkedIn](https://linkedin.com)")


# ── Main area ─────────────────────────────────────────────────────────────────
st.markdown("# 📈 AI Financial Analysis Chatbot")
st.markdown("*Ask questions about financial data in plain English — no SQL, no spreadsheets.*")
st.markdown("---")

if st.session_state.df is None:
    # Landing state
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
        <div class="metric-card">
            <div class="value">NLP</div>
            <div class="label">Natural Language Queries</div>
        </div>""", unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class="metric-card">
            <div class="value">📊</div>
            <div class="label">Dynamic Charts</div>
        </div>""", unsafe_allow_html=True)
    with col3:
        st.markdown("""
        <div class="metric-card">
            <div class="value">⚡</div>
            <div class="label">Instant Analysis</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("### 👈 Upload a CSV or load sample data to get started")
    st.markdown("""
    **Expected CSV format:**
    | Company | Year | Revenue | Net_Income | EPS | Total_Assets | ... |
    |---------|------|---------|------------|-----|--------------|-----|
    | Apple   | 2023 | 383285  | 96995      | 6.13| 352583       | ... |
    """)
    st.stop()

# ── Data loaded — show KPI strip ─────────────────────────────────────────────
df = st.session_state.df
latest = df.sort_values("Year").groupby("Company").last().reset_index()

kpi_cols = st.columns(len(latest))
for i, (_, row) in enumerate(latest.iterrows()):
    with kpi_cols[i]:
        rev = f"${row['Revenue']/1000:.1f}B" if row['Revenue'] > 999 else f"${row['Revenue']:.0f}M"
        margin = (row['Net_Income'] / row['Revenue'] * 100)
        st.markdown(f"""
        <div class="metric-card">
            <div class="value">{rev}</div>
            <div class="label">{row['Company']} Revenue ({int(row['Year'])})</div>
            <div style="color:#3fb950;font-size:0.8rem;margin-top:4px">
                {margin:.1f}% net margin
            </div>
        </div>""", unsafe_allow_html=True)

st.markdown("---")

# ── Sample questions ──────────────────────────────────────────────────────────
companies = df["Company"].unique().tolist()
samples   = get_sample_questions(companies)
st.markdown("**💡 Try asking:**")
cols = st.columns(4)
for i, q in enumerate(samples):
    with cols[i % 4]:
        if st.button(q, key=f"sample_{i}"):
            st.session_state.pending_query = q

st.markdown("---")

# ── Chat history ──────────────────────────────────────────────────────────────
for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(f'<div class="chat-bubble-user">🧑 {msg["content"]}</div>',
                    unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="chat-bubble-bot">🤖 {msg["content"]}</div>',
                    unsafe_allow_html=True)
        if msg.get("chart"):
            st.plotly_chart(msg["chart"], use_container_width=True)

# ── Input bar ─────────────────────────────────────────────────────────────────
input_col, btn_col = st.columns([5, 1])
with input_col:
    default_val = st.session_state.pending_query
    user_input  = st.text_input(
        "Ask a financial question:",
        value=default_val,
        placeholder="e.g. Compare Apple and Tesla revenue in 2023",
        label_visibility="collapsed",
        key="query_input",
    )
with btn_col:
    ask_btn = st.button("Ask →", use_container_width=True)

# Clear pending after render
if st.session_state.pending_query:
    st.session_state.pending_query = ""

# ── Process query ─────────────────────────────────────────────────────────────
if (ask_btn or user_input) and user_input.strip():
    query = user_input.strip()
    st.session_state.messages.append({"role": "user", "content": query})

    with st.spinner("Analyzing..."):
        answer, chart = answer_query(query, df)

    st.session_state.messages.append({
        "role": "bot", "content": answer, "chart": chart
    })
    st.rerun()

# ── Clear chat ────────────────────────────────────────────────────────────────
if st.session_state.messages:
    if st.button("🗑 Clear chat"):
        st.session_state.messages = []
        st.rerun()
