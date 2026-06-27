import json
from database.db import get_cursor


def log_chat(user_id: int, message: str, response: str, mode: str = "general", search_queries: list = None) -> bool:
    queries_json = json.dumps(search_queries or [], ensure_ascii=False)
    try:
        with get_cursor() as cur:
            cur.execute(
                "INSERT INTO chat_logs (user_id, message, response, mode, search_queries) VALUES (?, ?, ?, ?, ?)",
                (user_id, message, response, mode, queries_json),
            )
        return True
    except Exception:
        return False


def log_quiz_result(user_id: int, question: str, answer: str, is_correct: bool, topic: str) -> bool:
    try:
        with get_cursor() as cur:
            cur.execute(
                "INSERT INTO quiz_results (user_id, question, answer, is_correct, topic) VALUES (?, ?, ?, ?, ?)",
                (user_id, question, answer, int(is_correct), topic),
            )
        return True
    except Exception:
        return False


def get_user_history(user_id: int, limit: int = 50) -> list[dict]:
    try:
        with get_cursor() as cur:
            cur.execute(
                "SELECT id, message, response, mode, timestamp, search_queries FROM chat_logs WHERE user_id = ? ORDER BY timestamp DESC LIMIT ?",
                (user_id, limit),
            )
            return [dict(row) for row in cur.fetchall()]
    except Exception:
        return []


def get_all_logs(limit: int = 200) -> list[dict]:
    try:
        with get_cursor() as cur:
            cur.execute(
                """
                SELECT cl.id, u.username, cl.message, cl.response, cl.mode, cl.timestamp, cl.search_queries
                FROM chat_logs cl
                JOIN users u ON u.id = cl.user_id
                ORDER BY cl.timestamp DESC
                LIMIT ?
                """,
                (limit,),
            )
            return [dict(row) for row in cur.fetchall()]
    except Exception:
        return []


def get_topic_stats() -> list[dict]:
    try:
        with get_cursor() as cur:
            cur.execute(
                "SELECT topic, COUNT(*) AS count FROM quiz_results GROUP BY topic ORDER BY count DESC LIMIT 20"
            )
            return [dict(row) for row in cur.fetchall()]
    except Exception:
        return []
