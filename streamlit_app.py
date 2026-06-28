import streamlit as st
import requests
import os

# ── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Finance Advisor AI",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

/* Background */
.stApp {
    background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
    min-height: 100vh;
}

/* Hide Streamlit chrome */
#MainMenu, footer, header { visibility: hidden; }

/* Sidebar */
[data-testid="stSidebar"] {
    background: rgba(15, 12, 41, 0.85) !important;
    backdrop-filter: blur(20px);
    border-right: 1px solid rgba(255,255,255,0.08);
}
[data-testid="stSidebar"] * { color: #e2e8f0 !important; }

/* Main block */
.main .block-container {
    padding: 1rem 2rem 2rem;
    max-width: 900px;
    margin: 0 auto;
}

/* Native chat messages - user */
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {
    background: rgba(109, 40, 217, 0.15) !important;
    border: 1px solid rgba(167, 139, 250, 0.2) !important;
    border-radius: 16px !important;
    margin: 0.4rem 0 !important;
}

/* Native chat messages - assistant */
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) {
    background: rgba(255, 255, 255, 0.04) !important;
    border: 1px solid rgba(255, 255, 255, 0.08) !important;
    border-radius: 16px !important;
    margin: 0.4rem 0 !important;
}

/* Chat message text color */
[data-testid="stChatMessage"] p,
[data-testid="stChatMessage"] li,
[data-testid="stChatMessage"] span {
    color: #f1f5f9 !important;
}

/* Chat input bar */
[data-testid="stChatInput"] {
    background: rgba(255,255,255,0.06) !important;
    border: 1px solid rgba(255,255,255,0.15) !important;
    border-radius: 14px !important;
}
[data-testid="stChatInput"] textarea {
    color: #f1f5f9 !important;
    font-family: 'Inter', sans-serif !important;
}
[data-testid="stChatInput"]:focus-within {
    border-color: rgba(167,139,250,0.6) !important;
    box-shadow: 0 0 0 3px rgba(167,139,250,0.15) !important;
}

/* Buttons */
.stButton > button {
    background: linear-gradient(135deg, #6d28d9, #2563eb) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    font-size: 0.85rem !important;
    transition: all 0.2s ease !important;
}
.stButton > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 20px rgba(109,40,217,0.4) !important;
}

/* Quick prompt chips */
.stButton > button[kind="secondary"] {
    background: rgba(255,255,255,0.06) !important;
    border: 1px solid rgba(255,255,255,0.12) !important;
    border-radius: 999px !important;
    font-size: 0.8rem !important;
    font-weight: 500 !important;
    padding: 0.3rem 0.8rem !important;
    color: #cbd5e1 !important;
}

/* Metric cards */
.metric-card {
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 14px;
    padding: 0.9rem 1rem;
    text-align: center;
    backdrop-filter: blur(10px);
}
.metric-card .label {
    font-size: 0.7rem;
    color: rgba(255,255,255,0.45);
    text-transform: uppercase;
    letter-spacing: 0.06em;
}
.metric-card .value {
    font-size: 1.5rem;
    font-weight: 700;
    color: #a78bfa;
    margin-top: 0.1rem;
}

/* Status badge */
.status-badge {
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    background: rgba(52,211,153,0.1);
    border: 1px solid rgba(52,211,153,0.25);
    color: #34d399;
    font-size: 0.75rem;
    font-weight: 600;
    padding: 0.3rem 0.8rem;
    border-radius: 999px;
}
.status-dot {
    width: 6px; height: 6px;
    background: #34d399;
    border-radius: 50%;
    animation: pulse-dot 2s infinite;
}

/* Hero */
.hero-header {
    text-align: center;
    padding: 1.5rem 0 0.5rem;
    animation: fadeInDown 0.5s ease;
}
.hero-header h1 {
    font-size: 2.2rem;
    font-weight: 700;
    background: linear-gradient(135deg, #a78bfa, #60a5fa, #34d399);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: 0.2rem;
}
.hero-header p {
    color: rgba(255,255,255,0.45);
    font-size: 0.9rem;
}

/* Divider */
hr.clean-divider {
    border: none;
    border-top: 1px solid rgba(255,255,255,0.07);
    margin: 0.8rem 0;
}

/* Animations */
@keyframes fadeInDown {
    from { opacity: 0; transform: translateY(-12px); }
    to   { opacity: 1; transform: translateY(0); }
}
@keyframes pulse-dot {
    0%, 100% { opacity: 1; }
    50%       { opacity: 0.35; }
}
</style>
""", unsafe_allow_html=True)

# ── Session State ─────────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []
if "message_count" not in st.session_state:
    st.session_state.message_count = 0
if "pending_prompt" not in st.session_state:
    st.session_state.pending_prompt = None

# ── Resolve API URL ───────────────────────────────────────────────────────────
def resolve_api_url() -> str:
    url = os.getenv("API_URL", "")
    if url and url.startswith("http"):
        return url
    try:
        url = st.secrets.get("API_URL", "")
        if url and url.startswith("http"):
            return url
    except Exception:
        pass
    return "http://localhost:8000"

# ── API Call ──────────────────────────────────────────────────────────────────
def call_api(query: str) -> str:
    base_url = st.session_state.get("api_url_input") or resolve_api_url()
    base_url = base_url.strip()
    if not base_url.startswith("http"):
        base_url = resolve_api_url()

    url = base_url.rstrip("/") + "/chat"
    try:
        resp = requests.post(
            url,
            json={"query": query},
            timeout=90,
            headers={"Content-Type": "application/json"},
        )
        if resp.status_code == 200:
            return resp.json().get("answer", "No response received.")
        elif resp.status_code == 503:
            return "⚠️ Model quota exhausted. Please try again later or check your Google GenAI limits."
        elif resp.status_code == 429:
            return "⏱️ Rate limit reached. Please wait a moment before sending another message."
        else:
            return f"❌ Server error ({resp.status_code}): {resp.text[:300]}"
    except requests.exceptions.ConnectionError:
        return "🔌 Cannot connect to the backend API. Make sure the Render service is running and the URL is correct."
    except requests.exceptions.Timeout:
        return "⏳ The request timed out. The backend may be waking up from sleep — please try again in a moment."
    except Exception as e:
        return f"❌ Unexpected error: {str(e)}"

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⚙️ Settings")

    default_url = resolve_api_url()
    st.text_input(
        "Backend API URL",
        value=default_url,
        help="Your Render FastAPI service URL",
        key="api_url_input",
    )

    st.markdown("---")
    st.markdown("### 🤖 Capabilities")
    st.markdown("""
- 📊 **Live Stock Prices** — any ticker
- 🏢 **Company Overview** — fundamentals
- 📐 **SIP Calculator** — future value
- 💳 **EMI Calculator** — loan planning
- 🎯 **Risk Profiler** — personalized score
- 💰 **Budget Planner** — 50/30/20 rule
- 📚 **Finance RAG** — document Q&A
    """)
    st.markdown("---")

    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="label">Messages</div>
            <div class="value">{st.session_state.message_count}</div>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown("""
        <div class="metric-card">
            <div class="label">Agents</div>
            <div class="value">3</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.message_count = 0
        st.rerun()

# ── Hero Header ───────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero-header">
    <h1>📈 Finance Advisor AI</h1>
    <p>Multi-agent intelligence for stocks, calculations & financial planning</p>
</div>
<div style="text-align:center; margin-bottom:1rem;">
    <span class="status-badge">
        <span class="status-dot"></span>
        3 Specialist Agents Active
    </span>
</div>
""", unsafe_allow_html=True)

# ── Quick Prompt Chips ────────────────────────────────────────────────────────
quick_prompts = [
    ("📊", "AAPL stock price"),
    ("🏢", "Tesla company overview"),
    ("📐", "SIP ₹5000/mo 12% 10yrs"),
    ("💳", "EMI ₹500000 9% 5yrs"),
    ("💰", "Budget for ₹80000/month"),
    ("🎯", "Risk profile age 28 moderate"),
]

cols = st.columns(len(quick_prompts))
for col, (emoji, label) in zip(cols, quick_prompts):
    with col:
        if st.button(f"{emoji} {label}", key=f"chip_{label}", use_container_width=True):
            st.session_state.pending_prompt = label
            st.rerun()

st.markdown("<hr class='clean-divider'>", unsafe_allow_html=True)

# ── Chat History (native components) ─────────────────────────────────────────
for msg in st.session_state.messages:
    with st.chat_message(msg["role"], avatar="🤖" if msg["role"] == "assistant" else "🧑"):
        st.markdown(msg["content"])

# ── Handle Pending Chip Prompt ────────────────────────────────────────────────
if st.session_state.pending_prompt:
    prompt = st.session_state.pending_prompt
    st.session_state.pending_prompt = None

    st.session_state.messages.append({"role": "user", "content": prompt})
    st.session_state.message_count += 1
    with st.chat_message("user", avatar="🧑"):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar="🤖"):
        with st.spinner("Thinking..."):
            answer = call_api(prompt)
        st.markdown(answer)

    st.session_state.messages.append({"role": "assistant", "content": answer})
    st.session_state.message_count += 1
    st.rerun()

# ── Chat Input (native — always pinned to bottom) ─────────────────────────────
if user_input := st.chat_input("Ask about stocks, SIP, EMI, budgeting, risk profile..."):
    st.session_state.messages.append({"role": "user", "content": user_input})
    st.session_state.message_count += 1

    with st.chat_message("user", avatar="🧑"):
        st.markdown(user_input)

    with st.chat_message("assistant", avatar="🤖"):
        with st.spinner("Thinking..."):
            answer = call_api(user_input)
        st.markdown(answer)

    st.session_state.messages.append({"role": "assistant", "content": answer})
    st.session_state.message_count += 1
    st.rerun()
