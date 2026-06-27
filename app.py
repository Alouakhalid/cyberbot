import streamlit as st

st.set_page_config(page_title="CyberEdu AI", page_icon="🛡️", layout="wide")

from database.db import init_db
from auth.auth_manager import init_admin_user

if "db_ready" not in st.session_state:
    init_db()
    init_admin_user()
    st.session_state["db_ready"] = True

from auth.session import load_session, is_admin

user = load_session()
page = st.session_state.get("page", "login")

if user is None:
    st.session_state["page"] = "login"
    from pages.login import show
    show()
elif page == "admin" and is_admin():
    from pages.admin import show
    show()
else:
    from pages.chat import show
    show()
