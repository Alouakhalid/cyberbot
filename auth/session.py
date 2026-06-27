import streamlit as st
from datetime import datetime, timedelta, timezone
from auth.auth_manager import verify_token
from database.db import get_cursor
from database.logger import get_user_history

_TOKEN_KEY   = "cb_token"
_USER_KEY    = "cb_user"
_MODE_KEY    = "cb_mode"
_HISTORY_KEY = "cb_chat_history"


def _save_token_to_db(user_id: int, token: str) -> None:
    expires_at = (datetime.now(timezone.utc) + timedelta(hours=24)).isoformat()
    try:
        with get_cursor() as cur:
            cur.execute("DELETE FROM sessions WHERE user_id = ?", (user_id,))
            cur.execute(
                "INSERT INTO sessions (user_id, token, expires_at) VALUES (?, ?, ?)",
                (user_id, token, expires_at),
            )
    except Exception:
        pass


def _delete_token_from_db(user_id: int) -> None:
    try:
        with get_cursor() as cur:
            cur.execute("DELETE FROM sessions WHERE user_id = ?", (user_id,))
    except Exception:
        pass


def save_session(token: str, user: dict) -> None:
    st.session_state[_TOKEN_KEY]   = token
    st.session_state[_USER_KEY]    = user
    st.session_state[_MODE_KEY]    = "general"
    st.session_state[_HISTORY_KEY] = []
    _save_token_to_db(user["id"], token)


def load_session() -> dict | None:
    token = st.session_state.get(_TOKEN_KEY)
    if not token:
        return None
    if not verify_token(token):
        clear_session()
        return None
    return st.session_state.get(_USER_KEY)


def clear_session() -> None:
    user = st.session_state.get(_USER_KEY)
    if user:
        _delete_token_from_db(user["id"])
    for key in [_TOKEN_KEY, _USER_KEY, _MODE_KEY, _HISTORY_KEY]:
        st.session_state.pop(key, None)


def is_logged_in() -> bool:
    return load_session() is not None


def is_admin() -> bool:
    user = st.session_state.get(_USER_KEY)
    if not user:
        return False
    return user.get("role") == "admin" or user.get("username").lower() == "admin"


def set_mode(mode: str) -> None:
    if mode in {"general", "red_team", "blue_team", "soc"}:
        st.session_state[_MODE_KEY] = mode


def get_mode() -> str:
    return st.session_state.get(_MODE_KEY, "general")


def add_to_chat_history(role: str, content: str) -> None:
    if _HISTORY_KEY not in st.session_state:
        st.session_state[_HISTORY_KEY] = []
    st.session_state[_HISTORY_KEY].append({"role": role, "content": content})


def get_chat_history() -> list[dict]:
    if _HISTORY_KEY not in st.session_state or not st.session_state[_HISTORY_KEY]:
        user = st.session_state.get(_USER_KEY)
        if user:
            db_hist = get_user_history(user["id"], limit=30)
            st.session_state[_HISTORY_KEY] = []
            for row in reversed(db_hist):
                if row.get("message"):
                    st.session_state[_HISTORY_KEY].append({"role": "user", "content": row["message"]})
                if row.get("response"):
                    st.session_state[_HISTORY_KEY].append({"role": "assistant", "content": row["response"]})
    return st.session_state.get(_HISTORY_KEY, [])


def clear_chat_history() -> None:
    st.session_state[_HISTORY_KEY] = []
