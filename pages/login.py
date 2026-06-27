import streamlit as st
from auth.auth_manager import register_user, login_user
from auth.session import save_session, is_logged_in

def _go(page):
    st.session_state["page"] = page
    st.rerun()

_CSS = """<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif !important; }
#MainMenu, footer, header, [data-testid="stToolbar"], [data-testid="stSidebarNav"], [data-testid="stSidebar"] { display: none !important; }

.stApp { background: #000000 !important; min-height: 100vh; }
.block-container { max-width: 400px !important; margin: 0 auto !important; padding: 60px 20px !important; }

/* Simple minimal form */
div[data-testid="stForm"] {
    background: #000000 !important;
    border: none !important;
    padding: 0 !important;
}

/* Inputs matching ChatGPT login */
.stTextInput > div > div > input {
    background: #2f2f2f !important;
    border: 1px solid #565869 !important;
    border-radius: 6px !important;
    color: #ececec !important;
    font-size: 16px !important;
    padding: 14px 16px !important;
}
.stTextInput > div > div > input:focus {
    border-color: #10a37f !important;
    box-shadow: 0 0 0 2px rgba(16,163,127,0.2) !important;
}
.stTextInput > label {
    color: #ffffff !important;
    font-size: 14px !important;
    font-weight: 500 !important;
    margin-bottom: 8px !important;
}

/* Button */
.stButton > button {
    background: #10a37f !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 6px !important;
    font-size: 16px !important;
    font-weight: 500 !important;
    padding: 12px !important;
    width: 100% !important;
    cursor: pointer !important;
    transition: background 0.2s !important;
}
.stButton > button:hover { background: #0d8a6a !important; }

/* Tabs */
.stTabs [data-baseweb="tab-list"] { background: transparent !important; border-bottom: 1px solid #333 !important; gap: 0 !important; }
.stTabs [data-baseweb="tab"] { color: #888 !important; font-size: 14px !important; font-weight: 500 !important; padding: 12px 24px !important; background: transparent !important; }
.stTabs [aria-selected="true"] { color: #fff !important; border-bottom: 2px solid #10a37f !important; }
[data-testid="stTabPanel"] { padding-top: 24px !important; }

.stAlert { border-radius: 6px !important; }
</style>"""

_LOGO = ('<div style="text-align:center;margin-bottom:40px">'
    '<svg viewBox="0 0 24 24" fill="none" style="width:48px;height:48px;margin:0 auto 24px;display:block">'
    '<path d="M12 2L3 7v9c0 5 4 8 9 10 5-2 9-5 9-10V7l-9-5z" stroke="#ffffff" stroke-width="2" stroke-linejoin="round"/>'
    '<circle cx="12" cy="12" r="3" fill="#ffffff" />'
    '</svg>'
    '<div style="font-size:32px;font-weight:700;color:#ffffff;margin-bottom:8px">Welcome back</div>'
    '</div>')

def show():
    st.markdown(_CSS, unsafe_allow_html=True)
    if is_logged_in():
        _go("chat")
        return

    st.markdown(_LOGO, unsafe_allow_html=True)

    tab_login, tab_register = st.tabs(["\u062a\u0633\u062c\u064a\u0644 \u0627\u0644\u062f\u062e\u0648\u0644", "\u062d\u0633\u0627\u0628 \u062c\u062f\u064a\u062f"])

    with tab_login:
        with st.form("login_form"):
            username = st.text_input("\u0627\u0633\u0645 \u0627\u0644\u0645\u0633\u062a\u062e\u062f\u0645", placeholder="")
            password = st.text_input("\u0643\u0644\u0645\u0629 \u0627\u0644\u0645\u0631\u0648\u0631", type="password", placeholder="")
            st.markdown('<br>', unsafe_allow_html=True)
            submitted = st.form_submit_button("Continue")
        if submitted:
            if not username or not password:
                st.error("\u0623\u062f\u062e\u0644 \u0627\u0633\u0645 \u0627\u0644\u0645\u0633\u062a\u062e\u062f\u0645 \u0648\u0643\u0644\u0645\u0629 \u0627\u0644\u0645\u0631\u0648\u0631.")
            else:
                with st.spinner("\u062c\u0627\u0631\u064d \u0627\u0644\u062a\u062d\u0642\u0642..."):
                    result = login_user(username, password)
                if result["success"]:
                    save_session(result["token"], result["user"])
                    _go("chat")
                else:
                    st.error(result["message"])

    with tab_register:
        with st.form("register_form"):
            r_user  = st.text_input("\u0627\u0633\u0645 \u0627\u0644\u0645\u0633\u062a\u062e\u062f\u0645", key="ru")
            r_email = st.text_input("\u0627\u0644\u0628\u0631\u064a\u062f \u0627\u0644\u0625\u0644\u0643\u062a\u0631\u0648\u0646\u064a", key="re")
            r_pass  = st.text_input("\u0643\u0644\u0645\u0629 \u0627\u0644\u0645\u0631\u0648\u0631", type="password", key="rp")
            r_pass2 = st.text_input("\u062a\u0623\u0643\u064a\u062f \u0643\u0644\u0645\u0629 \u0627\u0644\u0645\u0631\u0648\u0631", type="password", key="rp2")
            st.markdown('<br>', unsafe_allow_html=True)
            reg_sub = st.form_submit_button("Sign up")
        if reg_sub:
            if not all([r_user, r_email, r_pass, r_pass2]):
                st.error("\u0623\u0643\u0645\u0644 \u062c\u0645\u064a\u0639 \u0627\u0644\u062d\u0642\u0648\u0644.")
            elif r_pass != r_pass2:
                st.error("\u0643\u0644\u0645\u062a\u0627 \u0627\u0644\u0645\u0631\u0648\u0631 \u063a\u064a\u0631 \u0645\u062a\u0637\u0627\u0628\u0642\u062a\u064a\u0646.")
            elif len(r_pass) < 8:
                st.error("\u0643\u0644\u0645\u0629 \u0627\u0644\u0645\u0631\u0648\u0631 \u064a\u062c\u0628 \u0623\u0646 \u062a\u0643\u0648\u0646 8 \u0623\u062d\u0631\u0641 \u0639\u0644\u0649 \u0627\u0644\u0623\u0642\u0644.")
            else:
                with st.spinner("\u062c\u0627\u0631\u064d \u0625\u0646\u0634\u0627\u0621 \u0627\u0644\u062d\u0633\u0627\u0628..."):
                    result = register_user(r_user, r_email, r_pass)
                if result["success"]:
                    st.success(result["message"] + " \u2014 \u0633\u062c\u0651\u0644 \u062f\u062e\u0648\u0644\u0643 \u0627\u0644\u0622\u0646.")
                else:
                    st.error(result["message"])
