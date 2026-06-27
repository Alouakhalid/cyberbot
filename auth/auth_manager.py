import bcrypt
import jwt
import os
from datetime import datetime, timedelta, timezone
from database.db import get_cursor

try:
    import streamlit as st
    JWT_SECRET = st.secrets["JWT_SECRET"]
except Exception:
    JWT_SECRET = os.getenv("JWT_SECRET", "cyberbot_super_secret_change_me_in_prod")
JWT_ALGORITHM      = "HS256"
TOKEN_EXPIRY_HOURS = 24


def _hash_password(plain_password: str) -> str:
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(plain_password.encode(), salt).decode()


def _verify_password(plain_password: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain_password.encode(), hashed.encode())


def _create_token(user_id: int, username: str, role: str) -> str:
    payload = {
        "user_id":  user_id,
        "username": username,
        "role":     role,
        "exp":      datetime.now(timezone.utc) + timedelta(hours=TOKEN_EXPIRY_HOURS),
        "iat":      datetime.now(timezone.utc),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def verify_token(token: str) -> dict | None:
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def register_user(username: str, email: str, password: str, role: str = "student") -> dict:
    if len(password) < 8:
        return {"success": False, "message": "الباسورد لازم يكون 8 حروف على الأقل."}

    try:
        with get_cursor() as cur:
            cur.execute(
                "INSERT INTO users (username, email, password_hash, role) VALUES (?, ?, ?, ?)",
                (username.strip(), email.strip().lower(), _hash_password(password), role),
            )
        return {"success": True, "message": "تم التسجيل بنجاح! 🎉"}
    except Exception as e:
        msg = str(e)
        if "users.username" in msg:
            return {"success": False, "message": "اسم المستخدم ده موجود بالفعل."}
        if "users.email" in msg:
            return {"success": False, "message": "الإيميل ده مسجل بالفعل."}
        return {"success": False, "message": f"خطأ في التسجيل: {msg}"}


def login_user(username: str, password: str) -> dict:
    try:
        with get_cursor() as cur:
            cur.execute(
                "SELECT id, username, email, password_hash, role, is_active FROM users WHERE username = ?",
                (username.strip(),),
            )
            user = cur.fetchone()
    except Exception as e:
        return {"success": False, "message": f"خطأ في قاعدة البيانات: {e}"}

    if not user:
        return {"success": False, "message": "اسم المستخدم أو الباسورد غلط."}

    if not user["is_active"]:
        return {"success": False, "message": "⛔ الحساب ده محظور. تواصل مع الأدمن."}

    if not _verify_password(password, user["password_hash"]):
        return {"success": False, "message": "اسم المستخدم أو الباسورد غلط."}

    token = _create_token(user["id"], user["username"], user["role"])
    return {
        "success": True,
        "token":   token,
        "user": {
            "id":       user["id"],
            "username": user["username"],
            "email":    user["email"],
            "role":     user["role"],
        },
    }


def get_user_by_id(user_id: int) -> dict | None:
    try:
        with get_cursor() as cur:
            cur.execute(
                "SELECT id, username, email, role, created_at, is_active FROM users WHERE id = ?",
                (user_id,),
            )
            row = cur.fetchone()
            return dict(row) if row else None
    except Exception:
        return None


def get_all_users() -> list[dict]:
    try:
        with get_cursor() as cur:
            cur.execute(
                "SELECT id, username, email, role, created_at, is_active FROM users ORDER BY created_at DESC"
            )
            return [dict(row) for row in cur.fetchall()]
    except Exception:
        return []


def toggle_user_status(user_id: int) -> dict:
    try:
        with get_cursor() as cur:
            cur.execute("SELECT is_active FROM users WHERE id = ?", (user_id,))
            row = cur.fetchone()
            if not row:
                return {"success": False, "message": "المستخدم مش موجود."}
            new_status = 0 if row["is_active"] else 1
            cur.execute("UPDATE users SET is_active = ? WHERE id = ?", (new_status, user_id))
        label = "فُعِّل ✅" if new_status else "حُظِر ⛔"
        return {"success": True, "is_active": bool(new_status), "message": f"الحساب {label}"}
    except Exception as e:
        return {"success": False, "message": f"خطأ: {e}"}
