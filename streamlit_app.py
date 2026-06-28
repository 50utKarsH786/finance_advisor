import streamlit as st
import requests
import time
import os


# ── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Finance Advisor AI",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS (Dark Glassmorphism Theme) ─────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

/* ── Root & Background ── */
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}
.stApp {
    background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
    min-height: 100vh;
}

/* ── Hide Streamlit chrome ── */
#MainMenu, footer, header { visibility: hidden; }

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: rgba(255, 255, 255, 0.04);
    backdrop-filter: blur(20px);
    border-right: 1px solid rgba(255, 255, 255, 0.08);
}
[data-testid="stSidebar"] * { color: #e2e8f0 !important; }

/* ── Main content area ── */
.main .block-container {
    padding: 1.5rem 2rem 2rem;
    max-width: 860px;
    margin: 0 auto;
}

/* ── Hero Header ── */
.hero-header {
    text-align: center;
    padding: 2rem 0 1rem;
    animation: fadeInDown 0.6s ease;
}
.hero-header h1 {
    font-size: 2.6rem;
    font-weight: 700;
    background: linear-gradient(135deg, #a78bfa, #60a5fa, #34d399);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: 0.3rem;
}
.hero-header p {
    color: rgba(255,255,255,0.5);
    font-size: 0.95rem;
    font-weight: 400;
}

/* ── Chat bubbles ── */
.chat-bubble {
    display: flex;
    gap: 0.75rem;
    margin: 0.75rem 0;
    animation: fadeInUp 0.3s ease;
}
.chat-bubble.user { flex-direction: row-reverse; }

.avatar {
    width: 36px;
    height: 36px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.1rem;
    flex-shrink: 0;
}
.avatar.ai   { background: linear-gradient(135deg, #6d28d9, #2563eb); }
.avatar.user { background: linear-gradient(135deg, #059669, #0891b2); }

.bubble-content {
    max-width: 75%;
    padding: 0.85rem 1.1rem;
    border-radius: 1.25rem;
    font-size: 0.92rem;
    line-height: 1.6;
    color: #f1f5f9;
}
.bubble-content.ai {
    background: rgba(255,255,255,0.07);
    border: 1px solid rgba(255,255,255,0.1);
    border-top-left-radius: 0.25rem;
    backdrop-filter: blur(10px);
}
.bubble-content.user {
    background: linear-gradient(135deg, rgba(109,40,217,0.6), rgba(37,99,235,0.6));
    border: 1px solid rgba(167,139,250,0.3);
    border-top-right-radius: 0.25rem;
}

/* ── Typing indicator ── */
.typing-indicator {
    display: flex;
    gap: 0.75rem;
    margin: 0.75rem 0;
    align-items: center;
}
.typing-dots {
    display: flex;
    gap: 4px;
    padding: 0.7rem 1rem;
    background: rgba(255,255,255,0.07);
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 1rem;
    backdrop-filter: blur(10px);
}
.typing-dots span {
    width: 8px;
    height: 8px;
    background: #a78bfa;
    border-radius: 50%;
    display: inline-block;
    animation: bounce 1.2s infinite;
}
.typing-dots span:nth-child(2) { animation-delay: 0.2s; }
.typing-dots span:nth-child(3) { animation-delay: 0.4s; }

/* ── Divider ── */
.chat-divider {
    border: none;
    border-top: 1px solid rgba(255,255,255,0.06);
    margin: 1.5rem 0;
}

/* ── Quick chips ── */
.chip-container { display: flex; flex-wrap: wrap; gap: 0.5rem; margin-bottom: 1rem; }

/* ── Input override ── */
.stTextInput input {
    background: rgba(255,255,255,0.06) !important;
    border: 1px solid rgba(255,255,255,0.12) !important;
    border-radius: 12px !important;
    color: #f1f5f9 !important;
    padding: 0.75rem 1rem !important;
    font-size: 0.92rem !important;
}
.stTextInput input:focus {
    border-color: rgba(167,139,250,0.6) !important;
    box-shadow: 0 0 0 3px rgba(167,139,250,0.15) !important;
}
.stButton > button {
    background: linear-gradient(135deg, #6d28d9, #2563eb) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    font-size: 0.9rem !important;
    padding: 0.6rem 1.4rem !important;
    transition: all 0.2s ease !important;
}
.stButton > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 20px rgba(109,40,217,0.4) !important;
}

/* ── Metric cards ── */
.metric-card {
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 14px;
    padding: 1rem 1.2rem;
    text-align: center;
    backdrop-filter: blur(10px);
}
.metric-card .label { font-size: 0.75rem; color: rgba(255,255,255,0.45); text-transform: uppercase; letter-spacing: 0.05em; }
.metric-card .value { font-size: 1.4rem; font-weight: 700; color: #a78bfa; margin-top: 0.15rem; }

/* ── Status badge ── */
.status-badge {
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    background: rgba(52,211,153,0.12);
    border: 1px solid rgba(52,211,153,0.25);
    color: #34d399;
    font-size: 0.78rem;
    font-weight: 600;
    padding: 0.3rem 0.75rem;
    border-radius: 999px;
    margin-bottom: 0.5rem;
}
.status-dot {
    width: 7px; height: 7px;
    background: #34d399;
    border-radius: 50%;
    animation: pulse-dot 2s infinite;
}

/* ── Animations ── */
@keyframes fadeInDown {
    from { opacity: 0; transform: translateY(-15px); }
    to   { opacity: 1; transform: translateY(0); }
}
@keyframes fadeInUp {
    from { opacity: 0; transform: translateY(10px); }
    to   { opacity: 1; transform: translateY(0); }
}
@keyframes bounce {
    0%, 60%, 100% { transform: translateY(0); }
    30%            { transform: translateY(-6px); }
}
@keyframes pulse-dot {
    0%, 100% { opacity: 1; }
    50%       { opacity: 0.4; }
}

/* ── Pin Input Form to Bottom ── */
div[data-testid="stForm"] {
    position: fixed;
    bottom: 20px;
    left: 50%;
    transform: translateX(-50%);
    width: 100%;
    max-width: 860px;
    background: linear-gradient(135deg, #0f0c29 0%, #1e1b4b 100%) !important;
    backdrop-filter: blur(20px);
    z-index: 999;
    padding: 1rem !important;
    border-radius: 16px !important;
    border: 1px solid rgba(255, 255, 255, 0.12) !important;
    box-shadow: 0 -10px 25px rgba(0, 0, 0, 0.5) !important;
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

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⚙️ Settings")

    # Resolve API URL safely: check environment variable first, then st.secrets, then default to localhost
    api_url_default = os.getenv("API_URL")
    if not api_url_default:
        try:
            api_url_default = st.secrets.get("API_URL", "http://localhost:8000")
        except Exception:
            api_url_default = "http://localhost:8000"

    api_url = st.text_input(
        "Backend API URL",
        value=api_url_default,
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

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="label">Messages</div>
            <div class="value">{st.session_state.message_count}</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
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
""", unsafe_allow_html=True)

st.markdown("""
<div style="text-align:center; margin-bottom: 1.5rem;">
    <span class="status-badge">
        <span class="status-dot"></span>
        3 Specialist Agents Active
    </span>
</div>
""", unsafe_allow_html=True)

# ── Quick Prompt Chips ────────────────────────────────────────────────────────
quick_prompts = [
    "📊 AAPL stock price",
    "🏢 Tesla company overview",
    "📐 SIP: ₹5000/mo, 12%, 10yrs",
    "💳 EMI: ₹500000, 9%, 5yrs",
    "💰 Budget for ₹80000/month",
    "🎯 Risk profile: age 28, moderate",
]

st.markdown("<div class='chip-container'>", unsafe_allow_html=True)
cols = st.columns(len(quick_prompts))
for i, (col, prompt) in enumerate(zip(cols, quick_prompts)):
    with col:
        if st.button(prompt, key=f"chip_{i}", use_container_width=True):
            st.session_state.pending_prompt = prompt
            st.rerun()
st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<hr class='chat-divider'>", unsafe_allow_html=True)

# ── Chat History ──────────────────────────────────────────────────────────────
def render_message(role: str, content: str):
    if role == "user":
        st.markdown(f"""
        <div class="chat-bubble user">
            <div class="avatar user">🧑</div>
            <div class="bubble-content user">{content}</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="chat-bubble ai">
            <div class="avatar ai">🤖</div>
            <div class="bubble-content ai">{content}</div>
        </div>
        """, unsafe_allow_html=True)

for msg in st.session_state.messages:
    render_message(msg["role"], msg["content"])

# ── API Call ──────────────────────────────────────────────────────────────────
def call_api(query: str, base_url: str) -> str:
    # Resolve and clean base URL, fallback if empty or invalid
    clean_base = base_url.strip() if base_url else ""
    if not clean_base or not clean_base.startswith("http"):
        clean_base = os.getenv("API_URL", "http://localhost:8000")
        if not clean_base.startswith("http"):
            clean_base = "http://localhost:8000"

    url = clean_base.rstrip("/") + "/chat"
    try:
        resp = requests.post(
            url,
            json={"query": query},
            timeout=60,
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
        return "⏳ The request timed out (60s). The backend may be waking up from sleep — please try again."
    except Exception as e:
        return f"❌ Unexpected error: {str(e)}"

# ── Process Prompt (chip or input) ───────────────────────────────────────────
def process_prompt(user_input: str):
    if not user_input.strip():
        return

    # Remove emoji prefix from chip prompts for the API call
    clean_input = user_input.strip()
    for emoji in ["📊 ", "🏢 ", "📐 ", "💳 ", "💰 ", "🎯 "]:
        if clean_input.startswith(emoji):
            clean_input = clean_input[len(emoji):]
            break

    st.session_state.messages.append({"role": "user", "content": user_input})
    st.session_state.message_count += 1

    # Render user bubble immediately
    render_message("user", user_input)

    # Typing indicator
    typing_placeholder = st.empty()
    typing_placeholder.markdown("""
    <div class="typing-indicator">
        <div class="avatar ai">🤖</div>
        <div class="typing-dots">
            <span></span><span></span><span></span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Call backend
    answer = call_api(clean_input, api_url)

    typing_placeholder.empty()

    st.session_state.messages.append({"role": "assistant", "content": answer})
    st.session_state.message_count += 1

    render_message("assistant", answer)

# ── Handle pending chip prompt ────────────────────────────────────────────────
if st.session_state.pending_prompt:
    pending = st.session_state.pending_prompt
    st.session_state.pending_prompt = None
    process_prompt(pending)

# ── Chat Input ────────────────────────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
with st.form(key="chat_form", clear_on_submit=True):
    col_input, col_btn = st.columns([5, 1])
    with col_input:
        user_input = st.text_input(
            label="Message",
            placeholder="Ask about stocks, SIP, EMI, budgeting, risk profile...",
            label_visibility="collapsed",
            key="chat_input",
        )
    with col_btn:
        submitted = st.form_submit_button("Send 🚀", use_container_width=True)

if submitted and user_input:
    process_prompt(user_input)

# Spacer at the bottom to prevent the pinned chat input from overlapping with the messages
st.markdown("<div style='height: 140px;'></div>", unsafe_allow_html=True)
