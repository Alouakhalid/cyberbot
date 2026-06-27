import streamlit as st
from auth.session import (
    load_session, clear_session, is_admin,
    set_mode, get_mode,
    add_to_chat_history, get_chat_history, clear_chat_history,
)
from engine.llm import ask_stream
from engine.classifier import classify_intent
from engine.search import search_cyber, format_search_context
from database.logger import log_chat

_CSS = """<style>
@import url("https://fonts.googleapis.com/css2?family=S%C3%B6hne:wght@400;500;600&display=swap");
*, *::before, *::after { box-sizing: border-box; }
html, body, .stApp, .stMarkdown, p, h1, h2, h3, h4, input, .stButton > button { font-family: 'Söhne', 'Inter', sans-serif !important; }
.material-symbols-rounded, .material-icons { font-family: 'Material Symbols Rounded', 'Material Icons' !important; }
html, body { margin: 0; padding: 0; background: #212121 !important; color: #ececec; }

footer, [data-testid="stSidebarNav"], [data-testid="stSidebarNavItems"], [data-testid="stDecoration"] { display: none !important; }
[data-testid="stHeader"], [data-testid="stToolbar"], header { background: transparent !important; box-shadow: none !important; }
[data-testid="collapsedControl"] { display: flex !important; background: transparent !important; color: #ececec !important; }
[data-testid="collapsedControl"] svg { fill: #ececec !important; }

.stApp { background: #212121 !important; }
.stApp > div { background: #212121 !important; }
.block-container { max-width: 800px !important; padding: 0 1rem 120px !important; margin: 0 auto; }

/* Sidebar exactly like ChatGPT */
[data-testid="stSidebar"] {
    background: #171717 !important;
    border-right: none !important;
    width: 260px !important; min-width: 260px !important; max-width: 260px !important;
}
[data-testid="stSidebar"] > div:first-child { padding: 8px !important; }

[data-testid="stSidebar"] .stButton > button {
    width: 100% !important; background: transparent !important; border: none !important;
    padding: 12px 14px !important; text-align: left !important; justify-content: flex-start !important;
    color: #ececec !important; font-size: 14px !important; font-weight: 500 !important;
    border-radius: 8px !important; transition: background 0.1s ease !important;
}
[data-testid="stSidebar"] .stButton > button:hover { background: #202123 !important; }

/* Chat messages */
.stChatMessage { background: transparent !important; border: none !important; padding: 24px 0 !important; }
[data-testid="stChatMessage"] { max-width: 768px !important; margin: 0 auto !important; }
[data-testid="stChatMessageContent"] p { font-size: 16px !important; line-height: 1.6 !important; color: #ececec !important; margin: 0 0 12px !important; }

[data-testid="stChatMessage"][data-testid*="user"] [data-testid="stChatMessageContent"] {
    background: #2f2f2f !important; padding: 12px 20px !important;
    border-radius: 18px !important; max-width: 70% !important; margin-left: auto !important;
}
[data-testid="stChatMessage"][data-testid*="user"] .stChatAvatar { display: none !important; }
[data-testid="stChatMessage"][data-testid*="assistant"] [data-testid="stChatMessageContent"] { color: #ececec !important; }

.stChatAvatar { background: #10a37f !important; width: 28px !important; height: 28px !important; border-radius: 4px !important; display: flex; align-items: center; justify-content: center; }
.stChatAvatar svg { width: 18px; height: 18px; fill: white; }

/* Code blocks */
[data-testid="stChatMessageContent"] pre {
    background: #000000 !important; border: none !important;
    border-radius: 8px !important; margin: 16px 0 !important; overflow: hidden !important;
}
[data-testid="stChatMessageContent"] pre code {
    display: block !important; padding: 16px !important; background: transparent !important;
    color: #e6edf3 !important; font-size: 14px !important; line-height: 1.5 !important;
    font-family: 'Söhne Mono', 'Menlo', monospace !important;
}
[data-testid="stChatMessageContent"] code:not(pre code) {
    background: #2f2f2f !important; color: #ececec !important;
    padding: 2px 6px !important; border-radius: 4px !important; font-size: 14px !important;
}

/* Chat Input */
[data-testid="stChatInput"] {
    position: fixed !important; bottom: 24px !important; left: 50% !important;
    transform: translateX(calc(-50% + 130px)) !important;
    width: 100% !important; max-width: 768px !important; z-index: 999 !important;
    background: transparent !important;
}
@media(max-width:768px) { [data-testid="stChatInput"] { transform: translateX(-50%) !important; max-width: 95% !important; } }

[data-testid="stChatInput"] > div {
    background: #2f2f2f !important; border: 1px solid #40414f !important;
    border-radius: 24px !important; padding: 4px 12px !important;
    box-shadow: none !important; transition: none !important;
}
[data-testid="stChatInput"] > div:focus-within { border-color: #565869 !important; }
[data-testid="stChatInput"] textarea { background: transparent !important; color: #ececec !important; font-size: 16px !important; padding: 12px 14px !important; }
[data-testid="stChatInput"] textarea::placeholder { color: #8e8ea0 !important; }

/* Starter cards */
.starter-card .stButton > button {
    background: transparent !important; border: 1px solid #565869 !important;
    border-radius: 12px !important; padding: 16px !important;
    color: #c5c5d2 !important; text-align: left !important; height: auto !important;
    min-height: 80px !important; font-size: 14px !important; line-height: 1.4 !important;
    transition: background 0.1s !important; white-space: normal !important;
}
.starter-card .stButton > button:hover { background: #2f2f2f !important; }

[data-testid="stSidebar"] hr { border-color: #4d4d4f !important; margin: 10px 0 !important; }
</style>"""

_GPT_AVATAR = ('<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">'
    '<path d="M22.2819 9.8211a5.9847 5.9847 0 0 0-.5157-4.9108 6.0462 6.0462 0 0 0-6.5098-2.9A6.0651 6.0651 0 0 0 4.9807 4.1818a5.9847 5.9847 0 0 0-3.9977 2.9 6.0462 6.0462 0 0 0 .7427 7.0966 5.98 5.98 0 0 0 .511 4.9107 6.051 6.051 0 0 0 6.5146 2.9001A5.9847 5.9847 0 0 0 13.2599 24a6.0557 6.0557 0 0 0 5.7718-4.2057 5.9847 5.9847 0 0 0 3.989-2.9 6.051 6.051 0 0 0-.7388-7.0732z" fill="#10a37f"/>'
    '<path d="M11.9546 12.0125c-.027 0-.0535-.0011-.08-.003l-4.7078-2.7176a.6738.6738 0 0 1-.3366-.5833v-5.435a.6738.6738 0 0 1 .3366-.5833l4.7078-2.7177a.6738.6738 0 0 1 .6732 0l4.7078 2.7177a.6738.6738 0 0 1 .3366.5833v5.435a.6738.6738 0 0 1-.3366.5833l-4.7078 2.7176a.6738.6738 0 0 1-.5932.003z" fill="#fff"/>'
    '</svg>')

_WELCOME_HTML = ('<div style="text-align:center;padding-top:20vh;margin-bottom:60px">'
    '<div style="width:72px;height:72px;margin:0 auto 24px;background:#ffffff;border-radius:50%;display:flex;align-items:center;justify-content:center">'
    '<svg viewBox="0 0 24 24" fill="none" style="width:40px;height:40px">'
    '<path d="M12 2L3 7v9c0 5 4 8 9 10 5-2 9-5 9-10V7l-9-5z" stroke="#000" stroke-width="1.5" stroke-linejoin="round"/>'
    '<circle cx="12" cy="12" r="3" fill="#000" />'
    '</svg></div>'
    '<div style="font-size:24px;font-weight:600;color:#ececec">How can I help you today?</div>'
    '</div>')


MODES = {
    "general":   "ChatGPT",
    "red_team":  "Red Team Analyst",
    "blue_team": "Blue Team Analyst",
    "soc":       "SOC Engineer",
}

STARTERS = [
    ("Explain SQL Injection", "What is SQL Injection? Explain with a simple example."),
    ("How Firewalls Work", "Can you explain how a firewall works in simple terms?"),
    ("Understanding CVEs", "What is a CVE and how do I read vulnerability reports?"),
    ("SOC & SIEM", "What is a Security Operations Center (SOC) and what is SIEM?"),
]

def show():
    st.markdown(_CSS, unsafe_allow_html=True)
    user = load_session()
    if not user:
        st.session_state["page"] = "login"
        st.rerun()
        return

    mode = get_mode()
    history = get_chat_history()

    with st.sidebar:
        st.markdown('<div style="padding:4px 8px">', unsafe_allow_html=True)
        if st.button("\u2795  New chat", key="new_chat"):
            clear_chat_history()
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

        for key, label in MODES.items():
            if st.button(label, key=f"m_{key}"):
                set_mode(key)
                st.rerun()

        if is_admin():
            st.divider()
            if st.button("\u2699\ufe0f  Settings", key="go_admin"):
                st.session_state["page"] = "admin"
                st.rerun()

        st.divider()
        st.markdown(f'<div style="padding:10px;font-size:14px;font-weight:500;color:#ececec">{user["username"]}</div>', unsafe_allow_html=True)
        if st.button("Log out", key="logout"):
            clear_session()
            st.session_state["page"] = "login"
            st.rerun()

    if not history:
        st.markdown(_WELCOME_HTML, unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        for i, (title, desc) in enumerate(STARTERS):
            with (c1 if i % 2 == 0 else c2):
                st.markdown('<div class="starter-card">', unsafe_allow_html=True)
                if st.button(f"{title}\n\n{desc}", key=f"s{i}"):
                    _send(desc, user, mode)
                st.markdown('</div>', unsafe_allow_html=True)
    else:
        for msg in history:
            avatar = _GPT_AVATAR if msg["role"] == "assistant" else "👤"
            with st.chat_message(msg["role"], avatar=avatar):
                st.markdown(msg["content"])

    prompt = st.chat_input("Message ChatGPT...")
    if prompt:
        _send(prompt, user, mode)

def _send(prompt: str, user: dict, mode: str):
    add_to_chat_history("user", prompt)
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)

    intent = classify_intent(prompt)["intent"]
    active = intent if mode == "general" else mode

    results = search_cyber(prompt, max_results=3)
    ctx = format_search_context(results)
    history = get_chat_history()

    msgs = []
    if ctx:
        msgs.append({"role": "system", "content": ctx})
    for m in history[:-1]:
        msgs.append({"role": m["role"], "content": m["content"]})
    msgs.append({"role": "user", "content": prompt})

    with st.chat_message("assistant", avatar=_GPT_AVATAR):
        ph, full = st.empty(), ""
        for chunk in ask_stream(msgs, active):
            full += chunk
            ph.markdown(full + "\u258c")
        ph.markdown(full)

    add_to_chat_history("assistant", full)
    log_chat(user["id"], prompt, full, active, [prompt])
    st.rerun()
