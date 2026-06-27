from database.db import get_cursor


LEVELS = {
    (0,  40):  "Beginner",
    (40, 70):  "Intermediate",
    (70, 90):  "Advanced",
    (90, 101): "Expert",
}


def _get_score(user_id: int) -> dict:
    try:
        with get_cursor() as cur:
            cur.execute(
                "SELECT COUNT(*) as total, SUM(is_correct) as correct FROM quiz_results WHERE user_id = ?",
                (user_id,),
            )
            row = cur.fetchone()
            total   = row["total"]   or 0
            correct = int(row["correct"] or 0)
            return {"total": total, "correct": correct}
    except Exception:
        return {"total": 0, "correct": 0}


def get_skill_level(user_id: int) -> str:
    data = _get_score(user_id)
    if data["total"] == 0:
        return "Beginner"
    pct = (data["correct"] / data["total"]) * 100
    for (low, high), label in LEVELS.items():
        if low <= pct < high:
            return label
    return "Beginner"


def get_user_stats(user_id: int) -> dict:
    data = _get_score(user_id)
    total   = data["total"]
    correct = data["correct"]
    pct     = round((correct / total) * 100, 1) if total > 0 else 0.0

    try:
        with get_cursor() as cur:
            cur.execute(
                "SELECT topic, COUNT(*) as count, SUM(is_correct) as correct FROM quiz_results WHERE user_id = ? GROUP BY topic ORDER BY count DESC",
                (user_id,),
            )
            topics = [dict(r) for r in cur.fetchall()]
    except Exception:
        topics = []

    try:
        with get_cursor() as cur:
            cur.execute(
                "SELECT COUNT(*) as total FROM chat_logs WHERE user_id = ?",
                (user_id,),
            )
            row = cur.fetchone()
            chat_count = row["total"] if row else 0
    except Exception:
        chat_count = 0

    return {
        "level":       get_skill_level(user_id),
        "total_quiz":  total,
        "correct":     correct,
        "accuracy":    pct,
        "chat_count":  chat_count,
        "topics":      topics,
    }


def get_weak_topics(user_id: int) -> list[str]:
    try:
        with get_cursor() as cur:
            cur.execute(
                """
                SELECT topic,
                       COUNT(*) as total,
                       SUM(is_correct) as correct
                FROM quiz_results
                WHERE user_id = ?
                GROUP BY topic
                HAVING total >= 2 AND (CAST(correct AS FLOAT) / total) < 0.5
                ORDER BY (CAST(correct AS FLOAT) / total) ASC
                LIMIT 5
                """,
                (user_id,),
            )
            return [row["topic"] for row in cur.fetchall()]
    except Exception:
        return []
